document.addEventListener('DOMContentLoaded', () => {
    detectBrowser();
    const copy_button = document.querySelector('#copyButton');
    if (copy_button) {
        copy_button.addEventListener('click', copyToClipboard);
    }
    const show_new_hadith_button = document.querySelector('#showNewHadith');
    if (show_new_hadith_button) {
        show_new_hadith_button.addEventListener('click', fetchNewHadith);
    }
});

async function fetchNewHadith() {
    const url = window.location.href + `/api/fetch-hadith?fetch-mode=random`;
    try {
        const response = await fetch(url);
        const json_response = await response.json();
        if (json_response) {
            if (response.ok) {
                const quoteEnglish = json_response.hadithEnglish || 'English version not available';
                const quoteArabic = json_response.hadithArabic || 'Arabic version not available';
                const bookName = json_response.bookName || 'Book name not available';
                const writerName = json_response.bookWriterName || 'Writer name not available';
                const source = `Source: ${bookName} by ${writerName}`;
                document.getElementById('quoteEnglish').textContent = quoteEnglish;
                document.getElementById('quoteArabic').textContent = quoteArabic;
                document.getElementById('source').textContent = source;
                document.getElementById("reference").value = json_response.reference;

                // Show the copy button after successful fetch
                document.getElementById('copyButton').style.display = 'flex';
            } else {
                document.getElementById('quoteEnglish').textContent = json_response.error;
                document.getElementById('quoteArabic').textContent = '';
                document.getElementById('source').textContent = '';
                document.getElementById("reference").value = '';
            }
        } else {
            document.getElementById('quoteEnglish').textContent = 'Somthing went wrong. Please try again later.';
            document.getElementById('quoteArabic').textContent = 'حدث خطأ ما. يرجى المحاولة مرة أخرى في وقت لاحق.';
            document.getElementById('source').textContent = '';
            document.getElementById("reference").value = '';
        }
    } catch (error) {
        console.error('Failed to fetch the hadith:', error);
        document.getElementById('quoteEnglish').textContent = 'Failed to fetch hadith. Please try again later.';
        document.getElementById('quoteArabic').textContent = 'حدث خطأ ما. يرجى المحاولة مرة أخرى في وقت لاحق.';
        document.getElementById('source').textContent = '';
        document.getElementById("reference").value = '';
    }
}

function detectBrowser() {
    const userAgent = navigator.userAgent;
    const isMobileOrTablet = /Mobi|Android|iPhone|iPad|Tablet|Mobile/i.test(userAgent);

    if (!isMobileOrTablet) {
        if (userAgent.includes("Chrome") && !userAgent.includes("Edg") && !userAgent.includes("OPR")) {
            document.getElementById('chrome-btn').style.display = 'inline-block';
        } else if (userAgent.includes("Firefox")) {
            document.getElementById('firefox-btn').style.display = 'inline-block';
        }
    }
}

async function copyToClipboard() {
    const quoteEnglish = document.getElementById('quoteEnglish').textContent;
    const quoteArabic = document.getElementById('quoteArabic').textContent;
    const source = document.getElementById('source').textContent;
    const textToCopy = `${quoteEnglish}\n\n${quoteArabic}\n\n${source}`;

    try {
        await navigator.clipboard.writeText(textToCopy);
        showNotification();
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
}

function showNotification() {
    const notification = document.getElementById('notification');
    notification.className = 'show';
    setTimeout(() => {
        notification.className = notification.className.replace('show', '');
    }, 3000);
}
