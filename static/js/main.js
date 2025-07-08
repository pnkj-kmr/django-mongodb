/**
 * MongoDB Blog - Custom JavaScript
 * Enhanced functionality for the blog application
 */

// DOM Content Loaded
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
  setupNewsletterForms();
  setupScrollToTop();
  setupSearchEnhancements();
  setupImageLazyLoading();
  setupTooltips();
  setupAnimations();
  setupThemeToggle();
}

/**
 * Newsletter subscription functionality
 */
function setupNewsletterForms() {
  // Footer newsletter form
  const footerForm = document.getElementById("newsletter-form");
  if (footerForm) {
    footerForm.addEventListener("submit", handleNewsletterSubmission);
  }

  // Home page newsletter form
  const homeForm = document.getElementById("home-newsletter-form");
  if (homeForm) {
    homeForm.addEventListener("submit", handleNewsletterSubmission);
  }
}

/**
 * Handle newsletter form submission
 */
function handleNewsletterSubmission(e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  const submitBtn = form.querySelector('button[type="submit"]');
  const messageDiv =
    form.parentNode.querySelector('[id*="message"]') ||
    document.getElementById("newsletter-message");

  // Show loading state
  setLoadingState(submitBtn, true);

  // Get CSRF token
  const csrfToken =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    getCookie("csrftoken");

  fetch("/newsletter/signup/", {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      setLoadingState(submitBtn, false);

      if (data.status === "success") {
        showMessage(messageDiv, data.message, "success");
        form.reset();

        // Confetti effect for success
        if (typeof confetti !== "undefined") {
          confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
          });
        }
      } else {
        showMessage(messageDiv, data.message, "warning");
      }
    })
    .catch((error) => {
      setLoadingState(submitBtn, false);
      console.error("Newsletter subscription error:", error);
      showMessage(messageDiv, "An error occurred. Please try again.", "danger");
    });
}

/**
 * Scroll to top functionality
 */
function setupScrollToTop() {
  // Create scroll to top button
  const scrollBtn = document.createElement("button");
  scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
  scrollBtn.className = "btn btn-primary position-fixed";
  scrollBtn.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    `;
  scrollBtn.setAttribute("aria-label", "Scroll to top");

  document.body.appendChild(scrollBtn);

  // Show/hide based on scroll position
  window.addEventListener("scroll", function () {
    if (window.pageYOffset > 300) {
      scrollBtn.style.opacity = "1";
      scrollBtn.style.visibility = "visible";
    } else {
      scrollBtn.style.opacity = "0";
      scrollBtn.style.visibility = "hidden";
    }
  });

  // Scroll to top on click
  scrollBtn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });
}

/**
 * Enhanced search functionality
 */
function setupSearchEnhancements() {
  const searchInput = document.querySelector('input[name="q"]');
  if (!searchInput) return;

  let searchTimeout;

  // Add search suggestions (if you implement them later)
  searchInput.addEventListener("input", function () {
    clearTimeout(searchTimeout);
    const query = this.value.trim();

    if (query.length > 2) {
      searchTimeout = setTimeout(() => {
        // You can implement search suggestions here
        console.log("Search suggestions for:", query);
      }, 300);
    }
  });

  // Keyboard shortcuts for search
  document.addEventListener("keydown", function (e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      searchInput.focus();
    }

    // Escape to clear search
    if (e.key === "Escape" && document.activeElement === searchInput) {
      searchInput.value = "";
      searchInput.blur();
    }
  });
}

/**
 * Lazy loading for images
 */
function setupImageLazyLoading() {
  if ("IntersectionObserver" in window) {
    const images = document.querySelectorAll("img[data-src]");
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove("lazy");
          imageObserver.unobserve(img);
        }
      });
    });

    images.forEach((img) => imageObserver.observe(img));
  }
}

/**
 * Initialize Bootstrap tooltips
 */
function setupTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Animation on scroll
 */
function setupAnimations() {
  if ("IntersectionObserver" in window) {
    const animatedElements = document.querySelectorAll(".animate-on-scroll");

    const animationObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("fade-in");
          }
        });
      },
      {
        threshold: 0.1,
      }
    );

    animatedElements.forEach((el) => animationObserver.observe(el));
  }
}

/**
 * Theme toggle functionality
 */
function setupThemeToggle() {
  // Check for saved theme preference or default to light mode
  const currentTheme = localStorage.getItem("theme") || "light";

  // Apply the saved theme
  if (currentTheme === "dark") {
    document.body.classList.add("dark-theme");
  }

  // Create theme toggle button (if needed)
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      document.body.classList.toggle("dark-theme");

      // Save theme preference
      const theme = document.body.classList.contains("dark-theme")
        ? "dark"
        : "light";
      localStorage.setItem("theme", theme);

      // Update button icon
      const icon = this.querySelector("i");
      if (theme === "dark") {
        icon.className = "bi bi-sun";
      } else {
        icon.className = "bi bi-moon";
      }
    });
  }
}

/**
 * Utility function to show loading state
 */
function setLoadingState(button, isLoading) {
  if (isLoading) {
    button.disabled = true;
    button.innerHTML =
      '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
  } else {
    button.disabled = false;
    // Restore original content based on button context
    if (
      button.closest("#newsletter-form") ||
      button.closest("#home-newsletter-form")
    ) {
      button.innerHTML = '<i class="bi bi-send me-1"></i>Subscribe';
    } else if (button.closest("#comment-form")) {
      button.innerHTML = '<i class="bi bi-send me-1"></i>Submit Comment';
    } else {
      button.innerHTML = "Submit";
    }
  }
}

/**
 * Utility function to show messages
 */
function showMessage(container, message, type = "info") {
  if (!container) return;

  const alertClass = `alert-${type}`;
  container.innerHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

  // Auto-hide success messages after 5 seconds
  if (type === "success") {
    setTimeout(() => {
      const alert = container.querySelector(".alert");
      if (alert) {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      }
    }, 5000);
  }
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
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
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showToast("Copied to clipboard!", "success");
    });
  } else {
    // Fallback for older browsers
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand("copy");
      showToast("Copied to clipboard!", "success");
    } catch (err) {
      showToast("Failed to copy", "error");
    }
    document.body.removeChild(textArea);
  }
}

/**
 * Show toast notification
 */
function showToast(message, type = "info") {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById("toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toast-container";
    toastContainer.className = "toast-container position-fixed top-0 end-0 p-3";
    toastContainer.style.zIndex = "1055";
    document.body.appendChild(toastContainer);
  }

  // Create toast
  const toastId = "toast-" + Date.now();
  const toast = document.createElement("div");
  toast.id = toastId;
  toast.className = `toast align-items-center text-white bg-${
    type === "error" ? "danger" : type
  } border-0`;
  toast.setAttribute("role", "alert");
  toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast"></button>
        </div>
    `;

  toastContainer.appendChild(toast);

  // Initialize and show toast
  const bsToast = new bootstrap.Toast(toast, {
    autohide: true,
    delay: 3000,
  });
  bsToast.show();

  // Remove toast element after it's hidden
  toast.addEventListener("hidden.bs.toast", () => {
    toast.remove();
  });
}

/**
 * Format relative time (time ago)
 */
function timeAgo(date) {
  const now = new Date();
  const secondsPast = (now.getTime() - date.getTime()) / 1000;

  if (secondsPast < 60) {
    return "just now";
  }
  if (secondsPast < 3600) {
    return Math.round(secondsPast / 60) + " minutes ago";
  }
  if (secondsPast <= 86400) {
    return Math.round(secondsPast / 3600) + " hours ago";
  }
  if (secondsPast <= 2592000) {
    return Math.round(secondsPast / 86400) + " days ago";
  }
  if (secondsPast <= 31536000) {
    return Math.round(secondsPast / 2592000) + " months ago";
  }
  return Math.round(secondsPast / 31536000) + " years ago";
}

/**
 * Debounce function
 */
function debounce(func, wait, immediate) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(this, args);
  };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Global error handler
 */
window.addEventListener("error", function (e) {
  console.error("Global error:", e.error);
  // You can send errors to a logging service here
});

/**
 * Handle unhandled promise rejections
 */
window.addEventListener("unhandledrejection", function (e) {
  console.error("Unhandled promise rejection:", e.reason);
  // You can send errors to a logging service here
});

/**
 * Export functions for global use
 */
window.BlogApp = {
  showMessage,
  showToast,
  copyToClipboard,
  timeAgo,
  debounce,
  throttle,
  setLoadingState,
};
