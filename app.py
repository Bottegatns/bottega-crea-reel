from pathlib import Path
import tempfile, os, base64, json
import streamlit.components.v1 as components
import streamlit as st
from editor import render
st.set_page_config(page_title='Tutta n’ata storia · Crea Reel',page_icon='🎬',layout='centered')
st.title('🎬 Crea Reel')
st.caption('Tutta n’ata storia · Bottega equosolidale')
st.write('Scegli i video, inserisci le scritte e premi **Crea Reel**. Nessuna installazione sul computer.')
if 'dbx_files' not in st.session_state: st.session_state.dbx_files=[]
with st.expander('☁️ Video da Dropbox (facoltativo)'):
    token=st.secrets.get('DROPBOX_ACCESS_TOKEN','') if hasattr(st,'secrets') else ''
    folder=st.text_input('Cartella',value='/Video Social nuovi arrivi')
    if not token:
        st.info('Per usare Dropbox, configura DROPBOX_ACCESS_TOKEN nelle impostazioni private dell’app online. Nel frattempo puoi caricare i video qui sotto.')
    if st.button('Aggiorna elenco Dropbox',disabled=not bool(token)):
        try:
            import dropbox
            dbx=dropbox.Dropbox(token,timeout=60)
            res=dbx.files_list_folder(folder); found=[]
            while True:
                found.extend((x.name,x.path_lower) for x in res.entries if isinstance(x,dropbox.files.FileMetadata) and x.name.lower().endswith(('.mp4','.mov','.m4v')))
                if not res.has_more:break
                res=dbx.files_list_folder_continue(res.cursor)
            st.session_state.dbx_files=found
            st.success(f'{len(found)} video trovati')
        except Exception as exc: st.error(f'Errore Dropbox: {exc}')
    options=[x[0] for x in st.session_state.dbx_files]
    selected=st.multiselect('Seleziona i video',options)
st.subheader('📹 Video da montare')
uploads=st.file_uploader('Carica uno o più video',type=['mp4','mov','m4v'],accept_multiple_files=True)
st.subheader('✨ Stile e testi')
style=st.radio('Stile', ['Funky e dinamico','Elegante e naturale','Promozioni'],horizontal=False)
defaults={'Funky e dinamico':'NOVITÀ IN BOTTEGA\nBIO & EQUOSOLIDALE\nSCOPRI LE OFFERTE','Elegante e naturale':'SCELTE CONSAPEVOLI\nPRODOTTI EQUOSOLIDALI\nTUTTA N’ATA STORIA','Promozioni':'PROMOZIONI IN BOTTEGA\nOFFERTE SPECIALI\nVIENI A TROVARCI'}
phrases=st.text_area('Una scritta per riga (una alla volta)',value=defaults[style],height=110)
length=st.slider('Durata massima',12,35,22)
if st.button('🎬 CREA REEL',type='primary',use_container_width=True):
    if not uploads and not selected: st.warning('Seleziona almeno un video.')
    else:
        try:
            with st.spinner('Montaggio in corso…'):
                with tempfile.TemporaryDirectory(prefix='bottega_') as tmp:
                    folderpath=Path(tmp); vids=[]
                    if selected:
                        import dropbox
                        dbx=dropbox.Dropbox(token,timeout=120)
                        mapping=dict(st.session_state.dbx_files)
                        for i,name in enumerate(selected):
                            dest=folderpath/f'dropbox_{i:02d}.mp4'
                            dbx.files_download_to_file(str(dest),mapping[name]);vids.append(dest)
                    for i,up in enumerate(uploads or []):
                        dest=folderpath/f'upload_{i:02d}{Path(up.name).suffix.lower()}'
                        dest.write_bytes(up.getbuffer());vids.append(dest)
                    out=folderpath/'reel.mp4'
                    render(vids,out,[x.strip().upper() for x in phrases.splitlines() if x.strip()],length)
                    st.session_state['mp4']=out.read_bytes()
            st.success('Reel pronto! Controlla l’anteprima.')
        except Exception as exc:st.error(f'Impossibile completare il montaggio: {exc}')
if 'mp4' in st.session_state:
    st.video(st.session_state.mp4)
    st.subheader('📲 Condividi su Instagram (Android)')
    st.caption('Dal telefono prova a condividere il file con Instagram. Se Instagram non compare o non apre le Storie, scarica il video e selezionalo dalla galleria in Instagram. La musica si aggiunge nell’editor di Instagram.')
    # Il browser deve supportare Web Share API con file; i browser incorporati
    # o gli iframe possono impedirne l’uso. Per questo rimane il download.
    payload = base64.b64encode(st.session_state.mp4).decode('ascii')
    filename = 'Tutta_n_ata_storia_Reel.mp4'
    share_html = f"""<!doctype html><html lang='it'><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<style>body{{margin:0;font-family:system-ui,sans-serif}}button{{width:100%;padding:15px 12px;border:0;border-radius:12px;background:#218454;color:white;font-weight:750;font-size:16px;cursor:pointer}}#status{{font-size:13px;color:#555;margin-top:9px;line-height:1.4}}</style></head>
<body><button id='share'>📲 CONDIVIDI VIDEO (ANDROID)</button><div id='status' role='status'></div>
<script>
const data={json.dumps(payload)};
const filename={json.dumps(filename)};
const status=document.getElementById('status');
document.getElementById('share').addEventListener('click',async()=>{{
  try {{
    if(!navigator.share) throw new Error('La condivisione diretta non è disponibile in questo browser.');
    const raw=atob(data); const bytes=new Uint8Array(raw.length);
    for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
    const file=new File([bytes],filename,{{type:'video/mp4'}});
    if(navigator.canShare && !navigator.canShare({{files:[file]}})) throw new Error('Il browser non permette di condividere questo video.');
    await navigator.share({{files:[file]}});
    status.textContent='Se hai scelto Instagram, completa la Storia nell’app e aggiungi la musica lì.';
  }} catch(err) {{
    status.textContent=err.name==='AbortError'?'Condivisione annullata.':(err.message||'Condivisione non disponibile.')+' Usa il pulsante Scarica Reel qui sotto.';
  }}
}});
</script></body></html>"""
    components.html(share_html, height=100, scrolling=False)
    st.download_button('⬇️ SCARICA REEL MP4',st.session_state.mp4,filename,mime='video/mp4',use_container_width=True)
