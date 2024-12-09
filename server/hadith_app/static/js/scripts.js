document.addEventListener('DOMContentLoaded', () => {
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
  const urlPrefix = window.location.origin + window.location.pathname;
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

  const currentURL = window.location.origin + window.location.pathname;
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
