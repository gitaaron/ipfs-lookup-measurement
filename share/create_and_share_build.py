import pickle
import os
import shutil
import glob
import traceback
import subprocess
from pathlib import Path


# accept 'OUTPUT' location as environment var
# create 'build' folder
# iterate over each folder in 'figs'
    # parse meta.p
    # copy entire contents of folder to build
    # write index.html that is a list of pngs to contents folder
# write an html file 'index.html' that is a list of links with date range linking to ./1/figs.html (a list of figs)

FIGS_ROOT_DIR = '../analysis/figs'

def printDate(d):
    return d.strftime('%d-%m-%Y %H:%M')

def toLink(name):
    return name.replace(' ', '_').lower()

def create_index_page(build_dir, meta_info_list):
    index_page = open(os.path.join(build_dir, 'home/index.html'), 'w')
    index_page.write("""
        <html>
            <body>
                <h1>IPFS Measurement Result Sets</h1>
                """)
    for meta_info in meta_info_list:
        index_page.write(f"""
            <a href="ipfs://{meta_info['cid']}">{printDate(meta_info['started_at'])} to {printDate(meta_info['ended_at'])}</a><br />
        """)

    index_page.write("""
        </body>
    </html>""")

def share_figs_folder_to_ipfs(target_figs_dir):
    cmd = f"""ipfs add -Qr {target_figs_dir}"""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        print(result.stderr)
        exit(1)

    cmd = f"""ipfs add -Qr --only-hash {target_figs_dir}"""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        print(result.stderr)
        exit(1)

    return result.stdout.decode().rstrip('\n')


def create_fig_page(figs_dir_name, target_figs_dir, meta_info):

    if 'sections' not in meta_info:
        return

    fig_page = open(os.path.join(target_figs_dir, 'index.html'), 'w')
    fig_page.write(f"""
    <html>
        <body>
            <h1>IPFS Measurement Figures</h1>
            <h2>{printDate(meta_info['started_at'])} to {printDate(meta_info['ended_at'])}</h2>
            <h2>Table of Contents</h2>
            <ul>
    """)

    for section_name, section_file_names in meta_info['sections'].items():
        fig_page.write(f'''
                <li><a href="#{toLink(section_name)}">{section_name}</a></li>
        ''')

    fig_page.write('</ul>')

    for section_name, section_file_names in meta_info['sections'].items():
        fig_page.write(f'''
            <h2 id="{toLink(section_name)}">{section_name}</h2>
        ''')
        for file_name in section_file_names:
            fig_page.write(f'''
                <img src="./{file_name}" /><br />
            ''')


    fig_page.write("""
        </body>
    </html>""")

    fig_page.close()

def share_home_to_ipfs(home_dir):
    cmd = f"""ipfs add -Qr {home_dir}"""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        print(result.stderr)
        exit(1)

    cmd = f"""ipfs add -Qr --only-hash {home_dir}"""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        print(result.stderr)
        exit(1)

    cid = result.stdout.decode().rstrip('\n')
    print(f"homedir cid: {cid}")
    return cid

def add_to_ipns(home_cid):
    cmd = f"""ipfs name publish --key=dht_lookup_key /ipfs/{home_cid}"""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        print(result.stderr)
        exit(1)

    print(result.stdout)


def create_build():
    build_dir = os.getenv('OUTPUT', 'build')
    figs_info_list = []
    home_dir = os.path.join(build_dir, 'home')
    Path(home_dir).mkdir(exist_ok=True, parents=True)
    figs_dir_list = [int(d) for d in os.listdir(FIGS_ROOT_DIR)]
    figs_dir_list.sort(reverse=True)
    for figs_dir in figs_dir_list:
        figs_dir = str(figs_dir)
        print('figs_dir : %s' % figs_dir)
        target_figs_dir = os.path.join(build_dir, figs_dir)
        source_figs_dir = os.path.join(FIGS_ROOT_DIR, figs_dir)
        # rm target if it exists
        if os.path.exists(target_figs_dir) and os.path.isdir(target_figs_dir):
            shutil.rmtree(target_figs_dir)
        shutil.copytree(source_figs_dir, target_figs_dir)
        try:
            figs_info = pickle.load(open(os.path.join(target_figs_dir, 'meta.p'), 'rb'))
            figs_info['name'] = figs_dir
            figs_info_list.append(figs_info)
            create_fig_page(figs_dir, target_figs_dir, figs_info)
            figs_info['cid'] = share_figs_folder_to_ipfs(target_figs_dir)
        except:
            traceback.print_exc()

    create_index_page(build_dir, figs_info_list)
    cid = share_home_to_ipfs(home_dir)
    add_to_ipns(cid)

if __name__=='__main__':
    create_build()
