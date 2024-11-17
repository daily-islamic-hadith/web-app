document.addEventListener('DOMContentLoaded', () => {
  detectBrowser();
  const ar_copy_button = document.querySelector('#arCopyButton');
  const en_copy_button = document.querySelector('#enCopyButton');

  ar_copy_button?.addEventListener('click', function () {
    copyToClipboard('ar');
  });

  en_copy_button?.addEventListener('click', function () {
    copyToClipboard('en');
  });

  const show_new_hadith_button = document.querySelector('#showNewHadith');
  if (show_new_hadith_button) {
    show_new_hadith_button.addEventListener('click', fetchNewHadith);
  }
});

async function fetchNewHadith() {
  const url = window.location.href + `/api/festch-hadith?fetch-mode=random`;
  const ar_copy_button = document.querySelector('#arCopyButton');
  const en_copy_button = document.querySelector('#enCopyButton');

  try {
    const response = await fetch(url);
    const json_response = await response.json();

    ar_copy_button.style.display = 'none';
    en_copy_button.style.display = 'none';
    if (json_response) {
      if (response.ok) {
        const hadithEnglish =
          json_response.hadithEnglish || 'English version not available';
        const hadithArabic =
          json_response.hadithArabic || 'Arabic version not available';
        const exp_ar = json_response.hadithExplanationArabic;
        const exp_en = json_response.hadithExplanationEnglish;
        const bookName = json_response.bookName || 'Book name not available';
        const writerName =
          json_response.bookWriterName || 'Writer name not available';
        const source = `Source: ${bookName} by ${writerName}`;
        document.getElementById('hadithEnglish').textContent = hadithEnglish;
        document.getElementById('hadithArabic').textContent = hadithArabic;
        document.getElementById('source').textContent = source;
        document.getElementById('reference').value = json_response.reference;
        document.getElementById('exp_en').textContent = exp_en
          ? exp_en
          : 'Explanation not found';
        document.getElementById('exp_ar').textContent = exp_ar
          ? exp_ar
          : 'لا يوجد تفسير';
        ar_copy_button.style.display = 'flex';
        en_copy_button.style.display = 'flex';
      } else {
        document.getElementById('hadithEnglish').textContent =
          json_response.error;
        document.getElementById('hadithArabic').textContent = '';
        document.getElementById('source').textContent = '';
        document.getElementById('reference').value = '';
        document.getElementById('exp_en').textContent = '';
        document.getElementById('exp_ar').textContent = '';
        ar_copy_button.style.display = 'none';
        en_copy_button.style.display = 'none';
      }
    } else {
      document.getElementById('hadithEnglish').textContent =
        'Somthing went wrong. Please try again later.';
      document.getElementById('hadithArabic').textContent =
        'حدث خطأ ما. يرجى المحاولة مرة أخرى في وقت لاحق.';
      document.getElementById('source').textContent = '';
      document.getElementById('reference').value = '';
      document.getElementById('exp_en').textContent = '';
      document.getElementById('exp_ar').textContent = '';
      ar_copy_button.style.display = 'none';
      en_copy_button.style.display = 'none';
    }
  } catch (error) {
    console.error('Failed to fetch the hadith:', error);
    document.getElementById('hadithEnglish').textContent =
      'Failed to fetch hadith. Please try again later.';
    document.getElementById('hadithArabic').textContent =
      'حدث خطأ ما. يرجى المحاولة مرة أخرى في وقت لاحق.';
    document.getElementById('source').textContent = '';
    document.getElementById('reference').value = '';
    document.getElementById('exp_en').textContent = '';
    document.getElementById('exp_ar').textContent = '';
    ar_copy_button.style.display = 'none';
    en_copy_button.style.display = 'none';
  }
}

function detectBrowser() {
  const userAgent = navigator.userAgent;
  const isMobileOrTablet = /Mobi|Android|iPhone|iPad|Tablet|Mobile/i.test(
    userAgent
  );

  if (!isMobileOrTablet) {
    if (
      userAgent.includes('Chrome') &&
      !userAgent.includes('Edg') &&
      !userAgent.includes('OPR')
    ) {
      document.getElementById('chrome-btn').style.display = 'inline-block';
    } else if (userAgent.includes('Firefox')) {
      document.getElementById('firefox-btn').style.display = 'inline-block';
    }
  }
}

async function copyToClipboard(lang) {
  const textElementId = lang === 'ar' ? 'hadithArabic' : 'hadithEnglish';
  const hadithExp = lang === 'ar' ? 'exp_ar' : 'exp_en';
  const expTitle = lang === 'ar' ? 'التفسير' : ' Explanation';

  const hadithContent = document.getElementById(textElementId)?.textContent;
  const sourceContent = document.getElementById('source')?.textContent;
  const expContent = document.getElementById(hadithExp)?.textContent;

  if (!hadithContent || !sourceContent) {
    console.error('Text or source content is missing. Cannot copy.');
    return;
  }

  const currentURL = window.location.href;
  const textToCopy = `${hadithContent}\n\n${expTitle}\n\n${expContent}\n\n${sourceContent}\n\n${currentURL}`;

  try {
    await navigator.clipboard.writeText(textToCopy);
    showNotification(lang);
  } catch (err) {
    console.error('Failed to copy text to clipboard:', err.message);
  }
}

function showNotification(lang) {
  const notification = document.getElementById('notification');

  notification.textContent =
    lang === 'en' ? 'Hadith copied to clipboard!' : '!تم نسخ الحديث';

  if (notification) {
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 3000);
  }
}
