/* EEG General Education literature search, using Europe PMC. */
(function(){
 const topic='EEG OR electroencephalogra* OR neurophysiolog* OR electrocorticogra* OR "evoked potential" OR "evoked potentials" OR "intraoperative monitoring"';
 const scope='(TITLE:('+topic+') OR ABSTRACT:('+topic+')) AND (SRC:MED OR SRC:PMC)';
 const aliases={seizure:'seizur*',seizures:'seizur*',epilepsy:'epilep*',epileptic:'epilep*',eeg:'EEG OR electroencephalogra*',electroencephalography:'EEG OR electroencephalogra*',neurophysiology:'neurophysiolog*',pediatric:'pediatric* OR paediatric* OR child* OR infant* OR adolescen*',pediatrics:'pediatric* OR paediatric* OR child* OR infant* OR adolescen*',paediatric:'pediatric* OR paediatric* OR child* OR infant* OR adolescen*',children:'child* OR pediatric* OR paediatric*',child:'child* OR pediatric* OR paediatric*',neonatal:'neonat* OR newborn*',newborn:'neonat* OR newborn*',artifact:'artifact* OR artefact*',artifacts:'artifact* OR artefact*',artefact:'artifact* OR artefact*'};
 const stops=new Set(['a','an','the','of','in','on','for','and','or','to','with','about','articles','article','research','studies','study']);
 function tokens(term){return term.normalize('NFKC').toLowerCase().match(/[\p{L}\p{N}]+/gu)||[];}
 function queryFor(term,mode){
  const words=tokens(term);
  if(!words.length)return null;
  if(mode==='keywords')return '('+words.map(w=>'"'+w+'"').join(' AND ')+') AND '+scope;
  const concepts=[];
  let text=words.join(' ');
  for(const [phrase,expr] of [['status epilepticus','"status epilepticus" OR NCSE'],['long term monitoring','"long term monitoring" OR "video EEG" OR "video electroencephalography"'],['evoked potentials','"evoked potentials" OR "evoked potential"']]){
   if(text.includes(phrase)){concepts.push(expr);text=text.replaceAll(phrase,' ');}
  }
  for(const word of tokens(text))if(!stops.has(word))concepts.push(aliases[word]||'"'+word+'"');
  if(!concepts.length)return null;
  return '('+[...new Set(concepts)].map(c=>'(TITLE:('+c+')^4 OR KW:('+c+')^2)').join(' AND ')+') AND '+scope;
 }
 function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text)e.textContent=text;return e;}
 function init(){
  const root=document.getElementById('eeg-literature-search');if(!root||root.dataset.ready)return;
  root.dataset.ready='true';
  const style=el('style');style.textContent=[
   '#eeg-literature-search{margin:18px 0 22px;padding:clamp(16px,3vw,24px);border:1px solid #31566c;border-radius:12px;background:#0c2d44;color:#f5f9fc}',
   '#eeg-literature-search h2{margin:0 0 10px;font-size:21px}',
   '#eeg-literature-search .els-note{color:#b9cdd9;font-size:13px;line-height:1.6;margin:10px 0}',
   '#eeg-literature-search label{display:block;min-width:0}',
   '#eeg-literature-search input[type=search]{width:100%;min-width:0;margin-top:8px;padding:12px;border:1px solid #547184;border-radius:8px;background:#071e2e;color:#fff;font:inherit;font-size:16px}',
   '#eeg-literature-search .els-modes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;border:0;padding:0;margin:16px 0}',
   '#eeg-literature-search legend{font-weight:700;margin-bottom:8px}',
   '#eeg-literature-search .els-option{display:grid;grid-template-columns:20px minmax(0,1fr);gap:6px 10px;border:1px solid #426477;border-radius:8px;padding:12px;cursor:pointer}',
   '#eeg-literature-search .els-option input{grid-row:span 2;width:18px;height:18px;margin:2px 0;accent-color:#69be28}',
   '#eeg-literature-search .els-option span{font-size:12px;line-height:1.5;color:#b9cdd9}',
   '#eeg-literature-search button{min-height:44px;border:1px solid #69be28;border-radius:8px;padding:10px 20px;font:inherit;font-weight:700;background:#69be28;color:#062138;cursor:pointer}',
   '#eeg-literature-search button:disabled{opacity:.7;cursor:wait}',
   '#eeg-literature-search :focus-visible{outline:3px solid #fff;outline-offset:3px}',
   '#eeg-literature-search .els-results{margin-top:20px}',
   '#eeg-literature-search .els-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}',
   '#eeg-literature-search article{padding:16px;border:1px solid #31566c;border-radius:9px;background:#082238;min-width:0;overflow-wrap:anywhere}',
   '#eeg-literature-search article h3{font-size:16px;line-height:1.5;margin:0 0 8px}',
   '#eeg-literature-search article p{color:#b9cdd9;font-size:12px;line-height:1.6;margin:6px 0}',
   '#eeg-literature-search article a{display:inline-flex;align-items:center;min-height:44px;color:#b8ed93;font-weight:700;margin-top:8px}',
   '#eeg-literature-search .els-more{display:block;width:100%;margin-top:14px;background:#0d3048;color:#c9f6a8}',
   '@media(max-width:650px){#eeg-literature-search .els-modes,#eeg-literature-search .els-grid{grid-template-columns:minmax(0,1fr)}}'
  ].join('\n');root.append(style);
  root.append(el('h2','','Search EEG and Neurophysiology Articles'));
  const form=el('form'),label=el('label','','Search research articles'),input=el('input');
  input.type='search';input.id='eeg-article-query';input.maxLength=200;input.required=true;input.placeholder='For example, neonatal seizures or EEG artifacts';label.htmlFor=input.id;label.append(input);
  const modes=el('fieldset','els-modes');modes.append(el('legend','','Search by'));
  for(const [value,title,description] of [['keywords','Keywords','Find words anywhere in indexed article content.'],['subject','Subject Matter','Focus on titles and subject keywords, including related clinical terms.']]){
   const option=el('label','els-option'),radio=el('input');radio.type='radio';radio.name='eeg-search-mode';radio.value=value;radio.checked=value==='subject';
   option.append(radio,el('strong','',title),el('span','',description));modes.append(option);
  }
  const submit=el('button','','Search');submit.type='submit';
  form.append(label,modes,submit);
  root.append(form,el('p','els-note','Searches EEG and related neurophysiology literature through Europe PMC. Subject Matter uses titles and subject keywords as indicators of the main topic; it does not assess the full article. Index coverage and article access vary. Reading an article does not independently award CEUs.'));
  const out=el('div','els-results');out.setAttribute('aria-live','polite');root.append(out);
  let state={items:[],total:0,next:null,term:'',mode:'subject',loading:false,error:'',started:false},controller,request=0;
  function paint(){
   out.replaceChildren();out.setAttribute('aria-busy',String(state.loading));submit.disabled=state.loading;
   if(!state.started){out.append(el('p','els-note','Enter a topic and select Search to see matching articles.'));return;}
   if(state.error)out.append(el('p','els-note',state.error));
   else out.append(el('p','els-note',state.loading&&!state.items.length?'Searching articles…':state.total+' '+(state.mode==='keywords'?'keyword':'subject')+' results for “'+state.term+'” · '+state.items.length+' shown'));
   const grid=el('div','els-grid');
   for(const item of state.items){
    const card=el('article');card.append(el('h3','',item.title||'Untitled article'));
    card.append(el('p','',[item.journalTitle,item.firstPublicationDate||item.pubYear].filter(Boolean).join(' · ')));
    if(item.authorString)card.append(el('p','',item.authorString));
    card.append(el('p','',item.isOpenAccess==='Y'?'Open access':'Check article access'));
    const link=el('a','','Read article ↗');
    link.href='https://europepmc.org/article/'+encodeURIComponent(item.source)+'/'+encodeURIComponent(item.id);
    link.target='_blank';link.rel='noopener noreferrer';card.append(link);grid.append(card);
   }
   out.append(grid);
   if(!state.loading&&!state.error&&state.total===0)out.append(el('p','els-note','No matching articles. Try a broader topic or switch to Keywords.'));
   if(state.next&&state.items.length<state.total){
    const more=el('button','els-more','See More ('+Math.max(0,state.total-state.items.length).toLocaleString()+' remaining)');more.type='button';more.disabled=state.loading;more.addEventListener('click',()=>search(state.term,true,state.mode));out.append(more);
   }
  }
  async function search(term,append,mode){
   if(controller)controller.abort();const id=++request;
   const query=queryFor(term,mode);
   if(!query){state={...state,started:true,error:'Enter at least one specific topic or keyword.',loading:false};paint();return;}
   controller=new AbortController();const active=controller,cursor=append?state.next:'*';
   state={...state,term,mode,started:true,loading:true,error:'',items:append?state.items:[],total:append?state.total:0,next:append?state.next:null};paint();
   const timeout=setTimeout(()=>active.abort(),20000);
   try{
    const params=new URLSearchParams({query,format:'json',pageSize:append?'5':'10',cursorMark:cursor||'*',resultType:'lite'});
    const response=await fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+params,{signal:active.signal});
    if(!response.ok)throw Error('Unavailable');
    const data=await response.json();if(id!==request)return;
    if(!Number.isFinite(data.hitCount)||!Array.isArray(data.resultList?.result))throw Error('Invalid response');
    const seen=new Set(state.items.map(r=>r.source+':'+r.id));
    const incoming=data.resultList.result.filter(r=>{const key=r.source+':'+r.id;if(!r.id||!['MED','PMC'].includes(r.source)||seen.has(key))return false;seen.add(key);return true;});
    state.items=[...state.items,...incoming];state.total=data.hitCount;
    state.next=incoming.length&&data.nextCursorMark!==cursor?data.nextCursorMark:null;
   }catch(error){if(id===request)state.error='Article search is temporarily unavailable. Please try again.';}
   finally{clearTimeout(timeout);if(id===request){state.loading=false;paint();}}
  }
  form.addEventListener('submit',event=>{event.preventDefault();const term=input.value.trim();if(term)search(term,false,form.querySelector('input[name="eeg-search-mode"]:checked').value);});
  paint();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
