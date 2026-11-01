from pathlib import Path
import tempfile, os
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
    st.download_button('⬇️ SCARICA REEL MP4',st.session_state.mp4,'Tutta_n_ata_storia_Reel.mp4',mime='video/mp4',use_container_width=True)
