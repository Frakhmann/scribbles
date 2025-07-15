const themeToggle = document.getElementById("toggle-theme");
const html = document.documentElement;
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {
    html.classList.add("dark");
}

themeToggle ?.addEventListener("click", () => {
    html.classList.toggle("dark");
    const isDark = html.classList.contains("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
});

// hghfghfj