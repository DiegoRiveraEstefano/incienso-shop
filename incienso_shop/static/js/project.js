/**
 * Incienso Shop - Client-Side Architecture
 * Vanilla JS, Unpoly 3 integration & Native Custom Elements (Web Components)
 */

// 1. Unpoly Configuration & CSRF Protection
document.addEventListener("DOMContentLoaded", () => {
  if (window.up) {
    // Enable CSRF token automatically from Django cookie
    const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };

    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      up.network.config.headers["X-CSRFToken"] = csrfToken;
    }

    // Default target for standard links
    up.link.config.followSelectors.push("a[up-follow]");
  }
});

// 2. Web Component: <incienso-aroma-badge>
class InciensoAromaBadge extends HTMLElement {
  connectedCallback() {
    const family = this.getAttribute("family") || "RESINAS";
    const labels = {
      RESINAS: { text: "Resinas Puras", icon: "bi-gem", class: "badge-resinas" },
      MADERAS: { text: "Maderas Sagradas", icon: "bi-tree", class: "badge-maderas" },
      FLORALES: { text: "Florales & Dulces", icon: "bi-flower1", class: "badge-florales" },
      HERBALES: { text: "Hierbas Sagradas", icon: "bi-droplet-half", class: "badge-herbales" },
      ESPECIADOS: { text: "Especiados Cálidos", icon: "bi-fire", class: "badge-especiados" },
      CITRICOS: { text: "Cítricos Frescos", icon: "bi-sun", class: "badge-citricos" },
    };

    const info = labels[family] || { text: family, icon: "bi-tag", class: "bg-light text-dark" };
    this.innerHTML = `
      <span class="badge ${info.class} px-2 py-1 rounded-pill small fw-semibold">
        <i class="bi ${info.icon} me-1"></i>${info.text}
      </span>
    `;
  }
}
customElements.define("incienso-aroma-badge", InciensoAromaBadge);

// 3. Web Component: <incienso-stock-counter>
class InciensoStockCounter extends HTMLElement {
  connectedCallback() {
    const stock = parseInt(this.getAttribute("stock") || "0", 10);
    if (stock > 5) {
      this.innerHTML = `<span class="badge bg-success bg-opacity-10 text-success border border-success-subtle">En Stock (${stock} disp.)</span>`;
    } else if (stock > 0) {
      this.innerHTML = `<span class="badge bg-warning bg-opacity-25 text-warning-emphasis border border-warning-subtle">¡Últimas ${stock} unidades!</span>`;
    } else {
      this.innerHTML = `<span class="badge bg-danger bg-opacity-10 text-danger border border-danger-subtle">Agotado Temporalmente</span>`;
    }
  }
}
customElements.define("incienso-stock-counter", InciensoStockCounter);

// 4. Web Component: <incienso-cart-badge>
class InciensoCartBadge extends HTMLElement {
  connectedCallback() {
    this.updateCount();
  }

  updateCount() {
    // Reads or updates cart count
    const count = this.getAttribute("count");
    if (count && parseInt(count, 10) > 0) {
      this.textContent = count;
      this.style.display = "inline-block";
    } else {
      this.style.display = "none";
    }
  }
}
customElements.define("incienso-cart-badge", InciensoCartBadge);
