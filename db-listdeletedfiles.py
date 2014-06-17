#!/usr/bin/env python2.7

APPKEYSECRETFILE = ".dblistdeletedfiles.appkey.p"
TOKENFILE=".dblistdeletedfiles.token.p"

# Include the Dropbox SDK
import dropbox, os, pickle

def getAppKeySecret():
	if os.path.isfile(APPKEYSECRETFILE):
		app_key, app_secret = pickle.load(open(APPKEYSECRETFILE, "rb"))
	else:
		app_key = raw_input("Enter the App Key: ").strip()
		app_secret = raw_input("Enter the App Secret: ").strip()
		pickle.dump((app_key, app_secret), open(APPKEYSECRETFILE, "wb"))
		
	return app_key, app_secret

def authorize():
	app_key, app_secret = getAppKeySecret()
	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
	authorize_url = flow.start()
	print '1. Go to: ' + authorize_url
	print '2. Click "Allow" (you might have to log in first)'
	print '3. Copy the authorization code.'
	code = raw_input("Enter the authorization code here: ").strip()
	return flow.finish(code)

def authenticate():
	if os.path.isfile(TOKENFILE):
		access_token = pickle.load(open(TOKENFILE, "rb"))
	else:
		(access_token, user_id) = authorize()
		pickle.dump(access_token, open(TOKENFILE, "wb"))
	client = dropbox.client.DropboxClient(access_token)
	return client


def read_directory(mypath, client):
	filelist = []
	my_folder = client.metadata(mypath, list=True, include_deleted=True)
	print "Processing folder %s" % mypath
	for i in my_folder["contents"]:
		if ("is_deleted" in i) and (i["is_deleted"]):
			print "found deleted file %s" % i["path"]
			filelist.append(i["path"])
		if i["is_dir"]:
			filelist.extend(read_directory(i["path"],client))
	return filelist


if __name__ == "__main__":
	client = authenticate()	

	deletedfiles = read_directory('/', client)
	outfile=file("deletedfiles.txt","w")
	outfile.write("%s\n" % item for item in deletedfiles)
	outfile.close()

