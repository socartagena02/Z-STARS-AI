document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("twoFactorModal");
    const openButton = document.getElementById("openTwoFactorModal");
    const closeButton = document.getElementById("closeTwoFactorModal");
    const cancelForm = document.getElementById("cancelTwoFactorForm");

    const manualToggle = document.getElementById("toggleManualKey");
    const manualContent = document.getElementById("manualKeyContent");

    const copyButton = document.getElementById("copySecretKey");
    const secretKey = document.getElementById("manualSecretKey");

    const codeInput = document.getElementById("twoFactorCode");

    function openModal() {
        if (!modal) return;
        modal.classList.add("modal-visible");
        document.body.classList.add("security-modal-open");
        setTimeout(() => codeInput?.focus(), 250);
    }

    function cancelSetup() {
        if (cancelForm) cancelForm.requestSubmit();
    }

    function closeModalVisual() {
        if (!modal) return;
        modal.classList.remove("modal-visible");
        document.body.classList.remove("security-modal-open");
    }

    if (modal) {
        openModal();
    }

    openButton?.addEventListener("click", openModal);

    closeButton?.addEventListener("click", cancelSetup);

    modal?.addEventListener("click", function (event) {
        if (event.target === modal) {
            cancelSetup();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && modal?.classList.contains("modal-visible")) {
            cancelSetup();
        }
    });

    manualToggle?.addEventListener("click", function () {
        const isHidden = manualContent.hidden;
        manualContent.hidden = !isHidden;
        manualToggle.classList.toggle("manual-open", isHidden);

        const chevron = manualToggle.querySelector(".manual-chevron");
        if (chevron) {
            chevron.classList.toggle("chevron-open", isHidden);
        }
    });

    copyButton?.addEventListener("click", async function () {
        if (!secretKey) return;

        try {
            await navigator.clipboard.writeText(secretKey.textContent.trim());
            copyButton.innerHTML = '<i class="bi bi-check-lg"></i>';
            copyButton.classList.add("copied");

            setTimeout(() => {
                copyButton.innerHTML = '<i class="bi bi-clipboard"></i>';
                copyButton.classList.remove("copied");
            }, 1800);
        } catch {
            copyButton.innerHTML = '<i class="bi bi-exclamation-circle"></i>';
        }
    });

    codeInput?.addEventListener("input", function () {
        this.value = this.value.replace(/\D/g, "").slice(0, 6);
    });

    const verifyForm = document.getElementById("verifyTwoFactorForm");
    verifyForm?.addEventListener("submit", function (event) {
        if (codeInput && codeInput.value.length !== 6) {
            event.preventDefault();
            codeInput.focus();
        }
    });
});