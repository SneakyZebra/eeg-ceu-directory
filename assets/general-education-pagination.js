/* General Education: ten initially, then five per click. */
(function(){
  function init(){
    const host=document.getElementById('general');
    if(!host||host.dataset.generalPagination==='ready')return;
    host.dataset.generalPagination='ready';
    const initial=10,increment=5;
    let visible=initial;
    const button=document.createElement('button');
    button.type='button';
    button.className='ceu-show-toggle';
    button.id='general-see-more';
    button.setAttribute('aria-controls','general');
    host.after(button);
    function cards(){return Array.from(host.children).filter(card=>card.classList.contains('entry'));}
    function update(){
      const entries=cards();
      entries.forEach((card,index)=>{card.style.display=index<visible?'':'none';});
      const remaining=Math.max(0,entries.length-visible);
      button.textContent='See More ('+remaining.toLocaleString()+' remaining)';
      button.style.display=remaining>0?'block':'none';
      button.setAttribute('aria-expanded',String(visible>initial));
    }
    button.addEventListener('click',()=>{
      visible=Math.min(cards().length,visible+increment);
      update();
    });
    new MutationObserver(update).observe(host,{childList:true});
    update();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
