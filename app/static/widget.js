/**
 * Embeddable Widget Script v1.0.0
 *
 * Usage: <script src="http://localhost:8000/widget.js?id=WIDGET_ID"></script>
 *
 * This script:
 * 1. Reads the widget ID from its own <script> tag's query string
 * 2. Fetches the widget config from the API
 * 3. Renders the form widget on the page
 * 4. Submits data via cross-origin fetch to the submission endpoint
 * 5. Includes a hidden honeypot field for spam detection
 */
(function () {
  "use strict";

  // ─── Find our script tag and extract the widget ID ───
  const scripts = document.getElementsByTagName("script");
  const currentScript = scripts[scripts.length - 1];
  const scriptSrc = currentScript.getAttribute("src");
  const urlParams = new URL(scriptSrc, window.location.href).searchParams;
  const widgetId = urlParams.get("id");

  if (!widgetId) {
    console.error("[Widget] Missing widget ID in script src");
    return;
  }

  // ─── Derive the API base URL from the script's origin ───
  const scriptUrl = new URL(scriptSrc, window.location.href);
  const API_BASE = scriptUrl.origin;

  // ─── Fetch widget config ───
  fetch(`${API_BASE}/api/widgets/${widgetId}/config`)
    .then((res) => {
      if (!res.ok) throw new Error(`Config fetch failed: ${res.status}`);
      return res.json();
    })
    .then((config) => renderWidget(config))
    .catch((err) => console.error("[Widget] Failed to load config:", err));

  // ─── Render the widget ───
  function renderWidget(config) {
    const container = document.createElement("div");
    container.id = `widget-${widgetId}`;
    container.style.cssText = `
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 400px;
      margin: 20px auto;
      padding: 24px;
      border-radius: ${config.display_options?.border_radius || "8px"};
      background: ${config.display_options?.background_color || "#FFFFFF"};
      color: ${config.display_options?.text_color || "#1F2937"};
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
      border: 1px solid #E5E7EB;
    `;

    // Title
    const title = document.createElement("h3");
    title.textContent = config.title;
    title.style.cssText = "margin: 0 0 8px 0; font-size: 18px; font-weight: 600;";
    container.appendChild(title);

    // Description
    if (config.description) {
      const desc = document.createElement("p");
      desc.textContent = config.description;
      desc.style.cssText =
        "margin: 0 0 16px 0; font-size: 14px; color: #6B7280;";
      container.appendChild(desc);
    }

    // Form
    const form = document.createElement("form");
    form.style.cssText = "display: flex; flex-direction: column; gap: 12px;";

    // Render form fields from config
    (config.form_fields || []).forEach((field) => {
      const wrapper = document.createElement("div");

      const label = document.createElement("label");
      label.textContent = field.label;
      label.style.cssText =
        "display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; color: #374151;";
      wrapper.appendChild(label);

      let input;
      if (field.field_type === "textarea") {
        input = document.createElement("textarea");
        input.rows = 3;
      } else {
        input = document.createElement("input");
        input.type = field.field_type || "text";
      }
      input.name = field.name;
      input.placeholder = field.placeholder || "";
      input.required = field.required;
      input.style.cssText = `
        width: 100%; padding: 8px 12px; border: 1px solid #D1D5DB;
        border-radius: 6px; font-size: 14px; box-sizing: border-box;
        outline: none; transition: border-color 0.15s;
      `;
      input.addEventListener("focus", () => (input.style.borderColor = config.display_options?.color || "#4F46E5"));
      input.addEventListener("blur", () => (input.style.borderColor = "#D1D5DB"));
      wrapper.appendChild(input);

      form.appendChild(wrapper);
    });

    // ─── Honeypot field (hidden — bots fill it, humans don't) ───
    const honeypot = document.createElement("input");
    honeypot.type = "text";
    honeypot.name = "website";
    honeypot.tabIndex = -1;
    honeypot.autocomplete = "off";
    honeypot.style.cssText =
      "position: absolute; left: -9999px; top: -9999px; opacity: 0; height: 0; width: 0;";
    form.appendChild(honeypot);

    // Submit button
    const btn = document.createElement("button");
    btn.type = "submit";
    btn.textContent = config.button_text || "Submit";
    btn.style.cssText = `
      padding: 10px 20px; border: none; border-radius: 6px;
      background: ${config.display_options?.color || "#4F46E5"}; color: #FFFFFF;
      font-size: 14px; font-weight: 600; cursor: pointer;
      transition: opacity 0.15s;
    `;
    btn.addEventListener("mouseenter", () => (btn.style.opacity = "0.9"));
    btn.addEventListener("mouseleave", () => (btn.style.opacity = "1"));
    form.appendChild(btn);

    // Status message area
    const status = document.createElement("div");
    status.style.cssText =
      "font-size: 13px; margin-top: 8px; min-height: 20px;";
    form.appendChild(status);

    // ─── Form submission handler ───
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      btn.disabled = true;
      btn.textContent = "Submitting...";
      status.textContent = "";

      const formData = new FormData(form);
      const data = {};
      formData.forEach((value, key) => {
        if (key !== "website") data[key] = value; // Exclude honeypot from data
      });

      try {
        const res = await fetch(`${API_BASE}/api/submissions/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            widget_id: widgetId,
            data: data,
            website: formData.get("website") || "", // Honeypot value
          }),
        });

        if (res.ok) {
          status.textContent = "✓ Submitted successfully!";
          status.style.color = "#059669";
          form.reset();
        } else {
          const err = await res.json().catch(() => ({}));
          status.textContent = err.detail || "Submission failed. Please try again.";
          status.style.color = "#DC2626";
        }
      } catch (err) {
        status.textContent = "Network error. Please try again.";
        status.style.color = "#DC2626";
      } finally {
        btn.disabled = false;
        btn.textContent = config.button_text || "Submit";
      }
    });

    container.appendChild(form);

    // Insert the widget into the page
    currentScript.parentNode.insertBefore(container, currentScript.nextSibling);
  }
})();
