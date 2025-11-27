// Main JS: dark mode and small anime.js intro
document.addEventListener('DOMContentLoaded', function(){
  const btn = document.getElementById('darkToggle');
  btn.addEventListener('click', ()=>{
    document.documentElement.classList.toggle('dark');
    btn.textContent = document.documentElement.classList.contains('dark') ? 'Light' : 'Dark';
  });

  // small hero animation
  if(window.anime){
    anime({
      targets: 'h1',
      translateY: [-10,0],
      opacity: [0,1],
      duration: 800,
      easing: 'easeOutQuad'
    });
  }
});
