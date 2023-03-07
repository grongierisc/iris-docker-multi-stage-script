import os
import logging
import shutil
import configparser
import argparse

# set logging file to /tmp/copy-data.log
logging.basicConfig(filename='/tmp/copy-data.log', level=logging.DEBUG)

def process_line(db_name,db_path ,data_dir):

    logging.info('db_name: {}, db_path: {}'.format(db_name, db_path))
    if not os.path.exists(db_path):
        logging.info('creating directory: {}'.format(db_path))
        # create the directory
        os.makedirs(db_path)
    logging.info('data_dir: {}'.format(data_dir))
    # join the data_dir path to the db_path
    source_db_path = os.path.join(data_dir, db_path[1:])
    logging.info('source_db_path: {}'.format(source_db_path))
    # force the copy of each file and directory
    # db_name to upper
    db_name = db_name.upper()
    if db_name not in ['IRISSYS', 'IRISLIB', 'IRISTEMP', 'IRISLOCALDATA', 'IRISAUDIT', 'ENSLIB', 'HSLIB', 'HSSYS' ]:
        # copy the directory
        logging.info('copying directory: {} to {}'.format(source_db_path, db_path))
        shutil.copytree(source_db_path, db_path, symlinks=True, ignore=None, dirs_exist_ok=True)
    elif db_name in ['IRISSYS', 'HSSYS', 'IRISLOCALDATA','IRISAUDIT','IRISTEMP']:
        # overwrite the file IRIS.DAT with the file from the data_dir
        logging.info('copying file: {} to {}'.format(os.path.join(source_db_path, 'IRIS.DAT'), os.path.join(db_path, 'IRIS.DAT')))
        shutil.copyfile(os.path.join(source_db_path, 'IRIS.DAT'), os.path.join(db_path, 'IRIS.DAT'))

def copy_data(iris_cpf_file, data_dir):
    # parse the iris.cpf file with configparser
    config = configparser.ConfigParser(strict=False, allow_no_value=True)
    config.read(iris_cpf_file)
    # get the [Databases] section
    dbs = config['Databases']
    for db_name, db_path in dbs.items():
        process_line(db_name, db_path, data_dir)

def csp_copy(csp_folders, data_dir):
    # copy the csp folders to the data_dir
    for csp_folder in csp_folders:
        logging.info('copying csp folder: {} to {}'.format(csp_folder, data_dir))
        shutil.copytree(csp_folder, os.path.join(data_dir, csp_folder), symlinks=True, ignore=None, dirs_exist_ok=True)

if __name__ == '__main__':
    # parse the command line arguments with argparse
    parser = argparse.ArgumentParser(description='Copy data from a directory to the IRIS data directory')
    # add the argument for the iris.cpf in the first position or -c or --cpf
    parser.add_argument('-c', '--cpf', help='path to the iris.cpf file')
    # add the argument for the data directory -d or --data_dir or can be at the second position
    parser.add_argument('-d', '--data_dir', help='path to the directory where the data files are located')
    # parse the arguments for csp folders
    parser.add_argument('--csp', help='path to the csp folders')
    # parse the arguments license file
    parser.add_argument('-l', '--license', help='path to the license file')
    args = parser.parse_args()
    # get the iris.cpf file
    iris_cpf_file = args.cpf
    # get the data directory
    data_dir = args.data_dir
    copy_data(iris_cpf_file, data_dir)
    # if the csp folders are defined, copy them to the data directory
    if args.csp:
        pass
    if args.license:
        pass
        # copy the license file to the data directory
        # license_file = 'usr/irissys/iris.key'
        # root_dir = '/'
        # dst = os.path.join(root_dir, license_file)
        # src = os.path.join(data_dir, license_file)
        # logging.info('copying license file: {} to {}'.format(src, dst))
        # shutil.copyfile(src, dst)
