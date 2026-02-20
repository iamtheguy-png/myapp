(function () {
  "use strict";

  var STORAGE_KEY = "expense-receipts-theme";
  var root = document.documentElement;
  var toggle = document.getElementById("theme-toggle");

  function getPreferred() {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "dark" || stored === "light") return stored;
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) return "dark";
    return "light";
  }

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  function init() {
    setTheme(getPreferred());
    if (toggle) {
      toggle.addEventListener("click", function () {
        var current = root.getAttribute("data-theme");
        setTheme(current === "dark" ? "light" : "dark");
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
