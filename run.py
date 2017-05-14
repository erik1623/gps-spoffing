import sys
import time
import wget
import os.path
import gzip
import argparse
# import zlib
import subprocess



def get_ephemeris(ephemeris_directory):
	global GZIP_DIR
	yday = time.localtime().tm_yday
	eFile = ephemeris_directory + '/brdc' + str(yday) + '0.17n'
	
	if not os.path.isfile(eFile):
		if not os.path.isfile(eFile + '.Z'):
			print 'get the ephemeris file\n\r'
			dFile = wget.download('http://ftp.pecny.cz/ftp/LDC/orbits/brdc/2017/brdc' + str(yday) + '0.17n.Z', './Files')
			print '\n\r' + dFile+ ' Downloaded\n\r'
		else:
			dFile = eFile + '.Z'
		print 'Uncompress...\n\r'
		subprocess.call(GZIP_DIR + '7z" e '+ dFile + ' -o' + ephemeris_directory, shell=True)
		print 'Finish to Uncompress\n\r'
	return eFile

def buildIQ(eFile, duration, csv_file):
	print eFile
	if csv_file is None:
		print '\nBuilding static location\n'
		subprocess.call('gps-sdr-sim -v -T now -e ' + eFile + ' -l 33.416111,35.857500,2800 -b 8 -d '+ duration + ' -s 4000000', shell=True)
	else:
		print '\nBuilding dynamic location according ' + csv_file + '\n'
		subprocess.call('gps-sdr-sim -v -T now -e ' + eFile + ' -u ' + csv_file + ' -b 8 -d '+ duration + ' -s 4000000', shell=True)
	return 'gpssim.bin\n\r'

	
def start_broadcast(binFile):
	global HACKRF_DIR 
	print 'HACKRF_DIR = ' + HACKRF_DIR
	print 'hackrf_transfer from ' + binFile + '\n\r'
	#subprocess.call([HACKRF_DIR + 'hackrf_transfer', '-t',  binFile,'-f', '1575420000', '-s', '4000000', '-a', '1', '-x', '1', '-R'],shell=True)
	subprocess.call(HACKRF_DIR + 'hackrf_transfer -t ' + binFile + ' -f 1575420000 -s 4000000 -a 1 -x 1 -R',shell=True)
def help():
	s = 'Environment settings\n'
	s += '\tEphemeris directory stored by default at ./Files. Can by set by EPHEREMIS_DIR\n'
	s += '\thackrf_transfer.exe location is set by default to "C:/Program Files/GNURadio-3.7/bin/". Can by set by HACKRF_DIR\n'
	s += '\t7z.exe location is set by default to "c:\\Program Files (x86)\\7-Zip\\7z". Can by set by GZIP_DIR\n'
	return s
	
def update_dirs():
	global FILES_DIR
	global HACKRF_DIR 
	global GZIP_DIR
	FILES_DIR = os.environ.get('FILES_DIR')
	HACKRF_DIR = os.environ.get('HACKRF_DIR')
	GZIP_DIR = os.environ.get('GZIP_DIR')
	
	if FILES_DIR is None:
		FILES_DIR = './Files'

	if HACKRF_DIR is None:
		HACKRF_DIR = '"C:/Program Files/GNURadio-3.7/bin/"'

	if GZIP_DIR is None:
		GZIP_DIR = 'c:\\Program Files (x86)\\7-Zip\\'
	
def main():
	global FILES_DIR
	global HACKRF_DIR 

	update_dirs()
	csv_file = None
	parser = argparse.ArgumentParser(description='Run.py')
	parser._optionals.title = help()
	parser.add_argument('-d', action="store", dest='duration', type=str, help='Running suration in seconds', default='300')
	parser.add_argument('-u', action="store", dest='csv_file', type=str, help='Set route csv file', default=None)
	results = parser.parse_args()

	ephemerisFile = get_ephemeris(FILES_DIR)
	print 'ephemerisFile = ' + ephemerisFile
	bin_file = buildIQ(ephemerisFile, results.duration, results.csv_file)
	start_broadcast(bin_file)

if __name__ == '__main__':
	main()
