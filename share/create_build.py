import pickle
import os
import shutil
import glob
import traceback

# accept 'OUTPUT' location as environment var
# create 'build' folder
# iterate over each folder in 'figs'
    # parse meta.p
    # copy entire contents of folder to build
    # write figs.html that is a list of pngs to contents folder
# write an html file 'index.html' that is a list of links with date range linking to ./1/figs.html (a list of figs)

FIGS_ROOT_DIR = '../analysis/figs'

def printDate(d):
    return d.strftime('%d-%m-%Y %H:%M')

def create_index_page(build_dir, meta_info_list):
    index_page = open(os.path.join(build_dir, 'index.html'), 'w')
    index_page.write("""
        <html>
            <body>
                <h1>DHT Lookup Results</h1>
                """)
    for meta_info in meta_info_list:
        index_page.write(f"""
            <a href="{meta_info['name']}/figs.html">{printDate(meta_info['started_at'])} to {printDate(meta_info['ended_at'])}</a><br />
        """)

    index_page.write("""
        </body>
    </html>""")

def create_fig_page(figs_dir_name, target_figs_dir, meta_info):
    fig_page = open(os.path.join(target_figs_dir, 'figs.html'), 'w')
    fig_page.write(f"""
    <html>
        <body>
            <h1>DHT Lookup Figures</h1>
            <h2>{printDate(meta_info['started_at'])} to {printDate(meta_info['ended_at'])}</h2>
    """)
    image_pat = r'%s/*.png' % target_figs_dir
    for fig in glob.glob(image_pat):
        figName = fig.split('/')[-1]
        fig_page.write(f'''
            <img src="/{os.path.join(figs_dir_name, figName)}" /><br />
        ''')

    fig_page.write("""
        </body>
    </html>""")

    fig_page.close()

def create_build():
    build_dir = os.getenv('OUTPUT', 'build')
    figs_info_list = []
    for figs_dir in os.listdir(FIGS_ROOT_DIR):
        print('figs_dir : %s' % figs_dir)
        target_figs_dir = os.path.join(build_dir, figs_dir)
        source_figs_dir = os.path.join(FIGS_ROOT_DIR, figs_dir)
        shutil.copytree(source_figs_dir, target_figs_dir, dirs_exist_ok=True)
        try:
            figs_info = pickle.load(open(os.path.join(target_figs_dir, 'meta.p'), 'rb'))
            figs_info['name'] = figs_dir
            figs_info_list.append(figs_info)
            create_fig_page(figs_dir, target_figs_dir, figs_info)
        except:
            traceback.print_exc()

    create_index_page(build_dir, figs_info_list)

if __name__=='__main__':
    create_build()
