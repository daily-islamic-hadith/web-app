document.addEventListener('DOMContentLoaded', () => {
  const applyDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(applyDarkMode);
  const ar_copy_button = document.querySelector('#arCopyButton');
  const en_copy_button = document.querySelector('#enCopyButton');
  const displayBtnMode = document.querySelector('#displayModeBtn');
  const show_new_hadith_button = document.querySelector('#showNewHadith');
  const share_button = document.querySelector('#shareHadith');
  displayBtnMode?.addEventListener('click', function () {
    applyTheme(!document.documentElement.classList.contains('dark'));
  });
  ar_copy_button?.addEventListener('click', function () {
    copyToClipboard('ar');
  });
  en_copy_button?.addEventListener('click', function () {
    copyToClipboard('en');
  });
  show_new_hadith_button?.addEventListener('click', fetchNewHadith);
  share_button?.addEventListener('click', shareHadithLink);

});

async function fetchNewHadith() {
  const urlPrefix = window.location.origin;
  const url = `${urlPrefix}/api/fetch-hadith?fetch-mode=random`;
  const arCopyButton = document.querySelector('#arCopyButton');
  const enCopyButton = document.querySelector('#enCopyButton');

  const elements = {
    hadithEnglish: document.getElementById('hadithEnglish'),
    hadithArabic: document.getElementById('hadithArabic'),
    source: document.getElementById('source'),
    reference: document.getElementById('reference'),
    expEn: document.getElementById('exp_en'),
    expAr: document.getElementById('exp_ar'),
  };

  const displayCopyButtons = (visible) => {
    const displayValue = visible ? 'flex' : 'none';
    if (arCopyButton) {
      arCopyButton.style.display = displayValue;
    }
    if (enCopyButton) {
      enCopyButton.style.display = displayValue;
    }
  };

  const setHadithContent = ({
    hadithEnglish = 'English version not available',
    hadithArabic = 'Arabic version not available',
    bookName = 'Book name not available',
    bookWriterName = 'Writer name not available',
    reference = '',
    hadithExplanationEnglish = 'Explanation not found',
    hadithExplanationArabic = 'لا يوجد تفسير',
  }) => {
    elements.hadithEnglish.textContent = hadithEnglish;
    elements.hadithArabic.textContent = hadithArabic;
    elements.source.textContent = `Source: ${bookName} by ${bookWriterName}`;
    elements.reference.value = reference;
    elements.expEn.textContent = hadithExplanationEnglish;
    elements.expAr.textContent = hadithExplanationArabic;
  };

  const clearContent = (errorMessageEn, errorMessageAr) => {
    setHadithContent({});
    elements.hadithEnglish.textContent = errorMessageEn;
    elements.hadithArabic.textContent = errorMessageAr;
    displayCopyButtons(false);
  };

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (response.ok && data) {
      setHadithContent(data);
      displayCopyButtons(true);
    } else {
      clearContent(
        data?.error || 'Something went wrong. Please try again later.',
        'حدث خطأ ما. يرجى المحاولة مرة أخرى في وقت لاحق.'
      );
    }
  } catch (error) {
    console.error('Failed to fetch the hadith:', error);
    clearContent(
      'Failed to fetch hadith. Please try again later.',
      'حدث خطأ ما. يرجى المحاولة مرة أخرى في وقت لاحق.'
    );
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
  const hadithPageUrl = window.location.origin + '/hadith/' + document.getElementById('reference').value;
  const textToCopy = `${hadithContent}\n\n${expTitle}\n\n${expContent}\n\n${sourceContent}\n\n${hadithPageUrl}`;

  try {
    await navigator.clipboard.writeText(textToCopy);
    showNotification(lang === 'en' ? 'Hadith copied to clipboard!' : '!تم نسخ الحديث');
  } catch (err) {
    console.error('Failed to copy text to clipboard:', err.message);
  }
}

async function shareHadithLink() {
  const hadithPageUrl = window.location.origin + '/hadith/' + document.getElementById('reference').value;
  try {
    await navigator.clipboard.writeText(hadithPageUrl);
    showNotification("URL copied to clipboard!");
  } catch (err) {
    console.error('Failed to copy text to clipboard:', err.message);
  }
}

function showNotification(text) {
  const notification = document.getElementById('notification');
  notification.textContent = text;
  if (notification) {
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 3000);
  }
}

function applyTheme(darkMode) {
  const displayModeBtn = document.querySelector("#displayModeBtn");
  if (darkMode) {
    document.documentElement.classList.remove('light');
    document.documentElement.classList.add('dark');
    displayModeBtn.title = "Switch to Light Mode";
    displayModeBtn.classList.remove('fa-moon');
    displayModeBtn.classList.add('fa-sun');
  } else {
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.add('light');
    displayModeBtn.title = "Switch to Dark Mode";
    displayModeBtn.classList.remove('fa-sun');
    displayModeBtn.classList.add('fa-moon');
  }
}
