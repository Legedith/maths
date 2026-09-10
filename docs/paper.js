window.MathJax = {
  tex: { inlineMath: [['\\(', '\\)']], displayMath: [['\\[', '\\]']] },
  options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] },
  chtml: { displayAlign: 'center' }
};
document.getElementById('print-paper').addEventListener('click', () => window.print());
