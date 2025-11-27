const socket = io();
let room = 'global';
if(typeof NOTE_ID !== 'undefined' && NOTE_ID){
  room = 'note-' + NOTE_ID;
}
socket.emit('join', {room});

const editor = document.getElementById('editor');
const status = document.getElementById('status');
const saveBtn = document.getElementById('saveBtn');
let timer = null;

function sendUpdate(){
  const content = editor.innerHTML;
  socket.emit('live_update', {room, content, note_id: NOTE_ID});
  status.textContent = 'Autosave: saved ' + new Date().toLocaleTimeString();
}

editor.addEventListener('input', ()=>{
  status.textContent = 'Autosave: typing...';
  if(timer) clearTimeout(timer);
  timer = setTimeout(sendUpdate, 1500);
});

socket.on('remote_update', data => {
  // apply remote changes without clobbering local cursor (simple approach)
  editor.innerHTML = data.content;
  status.textContent = 'Updated by collaborator';
});

saveBtn && saveBtn.addEventListener('click', ()=>{
  sendUpdate();
});
