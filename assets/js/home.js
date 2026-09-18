(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = window.matchMedia('(max-width: 760px)');
  const chapters = [...document.querySelectorAll('.chapter')];
  const images = [...document.querySelectorAll('.scene-image')];
  const links = [...document.querySelectorAll('.links a')];
  const hero = document.querySelector('.hero');
  const heroCopy = document.querySelector('.hero-copy');
  const heroPhoto = document.querySelector('.hero-photo');
  const progress = document.querySelector('.progress');
  const sceneLabel = document.querySelector('#scene-label');
  const sceneCount = document.querySelector('#scene-count');
  const clamp = (n, min = 0, max = 1) => Math.min(max, Math.max(min, n));
  let scheduled = false;
  let previousChapter = '';
  document.documentElement.classList.add('motion-ready');

  function render() {
    scheduled = false;
    const vh = window.innerHeight;
    const y = window.scrollY;
    const maxScroll = document.documentElement.scrollHeight - vh;
    progress.style.transform = `scaleX(${maxScroll > 0 ? clamp(y / maxScroll) : 0})`;
    const focusLine = vh * .55;
    let active = '';
    let currentChapter = chapters[0];
    chapters.forEach(section => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= focusLine && rect.bottom > focusLine) active = section.id;
    });
    chapters.forEach(chapter => {
      if (chapter.getBoundingClientRect().top <= focusLine) currentChapter = chapter;
    });
    document.body.dataset.chapter = active;
    links.forEach(link => {
      if (link.hash === `#${active}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    if (previousChapter !== currentChapter.id) {
      images.forEach(image => image.classList.toggle('active', image.dataset.scene === currentChapter.id));
      sceneLabel.textContent = currentChapter.dataset.label;
      sceneCount.textContent = `${currentChapter.dataset.number} / 03`;
      previousChapter = currentChapter.id;
    }
    const animate = !reducedMotion.matches && !mobile.matches;
    if (animate) {
      const heroProgress = clamp(y / (hero.offsetHeight * .7));
      heroCopy.style.transform = `translateY(${Math.min(y * .12, 90)}px)`;
      heroCopy.style.opacity = 1 - heroProgress * .8;
      heroPhoto.style.marginInline = `${5 * (1 - heroProgress)}vw`;
      heroPhoto.style.borderRadius = `${18 * (1 - heroProgress)}px`;
      heroPhoto.querySelector('img').style.transform = `scale(${1.08 - heroProgress * .08})`;
      const rect = currentChapter.getBoundingClientRect();
      const chapterProgress = clamp((vh - rect.top) / (vh + rect.height));
      images.forEach(image => { image.style.transform = `scale(1.09) translateY(${(chapterProgress - .5) * -4}%)`; });
    } else {
      heroCopy.style.transform = '';
      heroCopy.style.opacity = '';
      heroPhoto.style.marginInline = '';
      heroPhoto.style.borderRadius = '';
      heroPhoto.querySelector('img').style.transform = '';
      images.forEach(image => { image.style.transform = ''; });
    }
  }
  function schedule() {
    if (!scheduled) { scheduled = true; window.requestAnimationFrame(render); }
  }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  window.addEventListener('pageshow', schedule);
  reducedMotion.addEventListener('change', schedule);
  mobile.addEventListener('change', schedule);
  render();
})();
