// ======= Переключение темы =======

const themeToggle = document.getElementById("toggle-theme");
const html = document.documentElement;
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {
    html.classList.add("dark");
}

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        html.classList.toggle("dark");
        const isDark = html.classList.contains("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
    });
}

// ======= ЛАЙКИ =======
function bindLikeButtons() {
    const likeButtons = document.querySelectorAll(".like-btn");
    likeButtons.forEach(button => {
        button.onclick = async (e) => {
            e.preventDefault();
            const postId = button.getAttribute("data-post-id");
            const countSpan = document.getElementById(`like-count-${postId}`);
            const icon = document.getElementById(`like-icon-${postId}`);

            const response = await fetch("/likes/", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ post_id: parseInt(postId) })
            });

            if (response.ok) {
                const data = await response.json();
                countSpan.textContent = data.likes_count;

                if (data.liked) {
                    icon.classList.remove("bi-heart");
                    icon.classList.add("bi-heart-fill");
                } else {
                    icon.classList.remove("bi-heart-fill");
                    icon.classList.add("bi-heart");
                }
            } else {
                console.error("Ошибка при отправке лайка");
            }
        };
    });
}

async function updateLikeIcons() {
    const postIds = Array.from(document.querySelectorAll(".like-btn"))
        .map(btn => btn.getAttribute("data-post-id"))
        .filter(Boolean);

    let likedData = [];
    let likeCounts = {};

    if (postIds.length > 0) {
        // Получить все лайкнутые посты
        const response = await fetch("/likes/user-liked-posts", {
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                "Content-Type": "application/json"
            }
        });
        if (response.ok) {
            likedData = await response.json();
        }

        // Получить количество лайков для всех постов одним запросом
        const countsResp = await fetch(`/posts/batch-like-counts?ids=${postIds.join(",")}`);
        if (countsResp.ok) {
            likeCounts = await countsResp.json();
        }
    }

    // Обновить карточки
    document.querySelectorAll(".like-btn").forEach(button => {
        const postId = parseInt(button.getAttribute("data-post-id"));
        const icon = document.getElementById(`like-icon-${postId}`);
        const countSpan = document.getElementById(`like-count-${postId}`);
        if (!icon || !countSpan) return;
        if (likedData.includes(postId)) {
            icon.classList.remove("bi-heart");
            icon.classList.add("bi-heart-fill");
        } else {
            icon.classList.remove("bi-heart-fill");
            icon.classList.add("bi-heart");
        }
        // ВАЖНО: likeCounts[postId] может быть 0, надо проверять через hasOwnProperty!
        countSpan.textContent = Object.prototype.hasOwnProperty.call(likeCounts, postId) ? likeCounts[postId] : "0";
    });
}

// ======= REPORT POPUP =======
document.addEventListener('DOMContentLoaded', function () {
    // -------- ЛАЙКИ ----------
    bindLikeButtons();
    updateLikeIcons();
    window.addEventListener("pageshow", function () {
        updateLikeIcons();
    });

    // -------- ПРОВЕРКА АВТОРИЗАЦИИ ----------
    fetch("/auth/check", { credentials: "include" })
        .then(r => {
            if (r.status === 401) {
                window.location.replace("/auth/login");
            }
        });

    // -------- REPORT / ЖАЛОБЫ ----------
    let reportPopup = document.getElementById('report-popup');
    let reportForm = document.getElementById('report-form');
    let reportReason = document.getElementById('report-reason');
    let reportPostId = document.getElementById('report-post-id');
    let closePopup = document.getElementById('close-report-popup');
    let toast = document.getElementById('report-toast');

    if (reportPopup && reportForm && reportReason && reportPostId && closePopup && toast) {
        document.querySelectorAll('.report-btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                reportPostId.value = btn.getAttribute('data-post-id');
                reportReason.value = "";
                reportPopup.style.display = "flex";
                reportReason.focus();
            });
        });

        closePopup.addEventListener('click', function () {
            reportPopup.style.display = "none";
        });

        reportPopup.addEventListener('click', function (e) {
            if (e.target === reportPopup) reportPopup.style.display = "none";
        });

        reportForm.addEventListener('submit', function (e) {
            e.preventDefault();
            let reason = reportReason.value.trim();
            let postId = reportPostId.value;
            if (!reason || reason.length > 200) return;

            fetch('/posts/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ post_id: +postId, reason })
            })
                .then(resp => resp.json())
                .then(data => {
                    // вот сюда!
                    reportPopup.style.display = "none";
                    toast.classList.add("report-toast--show");
                    setTimeout(() => { toast.classList.remove("report-toast--show"); }, 2400);
                })
                .catch(() => {
                    alert('Something went wrong. Please try again.');
                });
        });

    }
});


