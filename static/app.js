const form = document.querySelector("#qr-form");
const urlInput = document.querySelector("#url");
const foreground = document.querySelector("#foreground");
const background = document.querySelector("#background");
const errorCorrection = document.querySelector("#error-correction");
const generateBtn = document.querySelector("#generate-btn");
const message = document.querySelector("#message");
const qrImage = document.querySelector("#qr-image");
const emptyState = document.querySelector("#empty-state");
const downloadBtn = document.querySelector("#download-btn");
const destination = document.querySelector("#destination");
const dimensions = document.querySelector("#dimensions");
const previewState = document.querySelector("#preview-state");
let currentImage = null;
let currentUrl = "";

function updateColorLabel(input, label) {
  document.querySelector(label).textContent = input.value.toUpperCase();
}
foreground.addEventListener("input", () => updateColorLabel(foreground, "#foreground-value"));
background.addEventListener("input", () => updateColorLabel(background, "#background-value"));

document.querySelector("#clear-url").addEventListener("click", () => {
  urlInput.value = "";
  urlInput.focus();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  message.className = "message";
  generateBtn.disabled = true;
  generateBtn.querySelector("span:first-child").textContent = "Generating…";
  previewState.textContent = "GENERATING";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        url: urlInput.value,
        foreground: foreground.value,
        background: background.value,
        errorCorrection: errorCorrection.value
      })
    });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || "Could not generate QR code.");

    currentImage = data.image;
    currentUrl = data.url;
    qrImage.src = currentImage;
    qrImage.hidden = false;
    emptyState.hidden = true;
    destination.textContent = currentUrl;
    destination.title = currentUrl;
    dimensions.textContent = data.dimensions;
    previewState.textContent = "READY TO SAVE";
    downloadBtn.disabled = false;
    message.textContent = "QR code generated successfully.";
    message.className = "message success";
  } catch (error) {
    previewState.textContent = currentImage ? "PREVIOUS QR" : "CHECK YOUR URL";
    message.textContent = error.message || "Something went wrong.";
  } finally {
    generateBtn.disabled = false;
    generateBtn.querySelector("span:first-child").textContent = "Generate QR code";
  }
});

downloadBtn.addEventListener("click", async () => {
  if (!currentImage) return;
  const hostApi = window.pywebview && window.pywebview.api;
  if (!hostApi || !hostApi.save_qr) {
    // Browser fallback, useful when the UI is opened during development.
    const link = document.createElement("a");
    link.href = currentImage;
    link.download = "qr-studio.png";
    link.click();
    return;
  }
  downloadBtn.disabled = true;
  const safeName = (new URL(currentUrl).hostname || "qr-code").replace(/[^a-z0-9.-]/gi, "_");
  try {
    const result = await hostApi.save_qr(currentImage, `${safeName}-qr.png`);
    if (result.ok) {
      message.textContent = "Saved successfully.";
      message.className = "message success";
    } else if (!result.cancelled) {
      message.textContent = result.message || "Could not save the QR code.";
      message.className = "message";
    }
  } catch (error) {
    message.textContent = "Could not open the save dialog. Try again.";
    message.className = "message";
  } finally {
    downloadBtn.disabled = false;
  }
});
