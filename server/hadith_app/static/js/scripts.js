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
  const url = `${window.location.href}/api/fetch-hadith?fetch-mode=random`;
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
    arCopyButton.style.display = displayValue;
    enCopyButton.style.display = displayValue;
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
  const hadithTitle = lang === 'ar' ? 'التفسير' : ' Explanation';

  const textContent = document.getElementById(textElementId)?.textContent;
  const sourceContent = document.getElementById('source')?.textContent;
  const hadithContent = document.getElementById(hadithExp)?.textContent;

  if (!textContent || !sourceContent) {
    console.error('Text or source content is missing. Cannot copy.');
    return;
  }

  const currentURL = window.location.href;
  const textToCopy = `${textContent}\n\n${hadithTitle}\n\n${hadithContent}\n\n${sourceContent}\n\n${currentURL}`;

  try {
    await navigator.clipboard.writeText(textToCopy);
    showNotification(lang);
  } catch (err) {
    console.error('Failed to copy text to clipboard:', err.message);
  }
}

function showNotification(lang) {
  const notification = document.getElementById(
    lang === 'en' ? 'enNotification' : 'arNotification'
  );

  if (notification) {
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 3000);
  }
}
