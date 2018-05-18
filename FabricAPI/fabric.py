import time
import urllib2
import json


class Fabric:
	class FabricConfig:
		def __init__(self):
			self.email = ''
			self.password = ''
			self.organizationID = ''
			self.appID = ''

	def __init__(self, config):
		self.config = config
		self.end = int(time.time())
		self.start = self.end - 1123200
		self.basicHeaders = {
		'user-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36', 
		'X-Requested-With':'XMLHttpRequest'
		}
		self.__checkConfig()

	def __checkConfig(self):
		if len(self.config.email) == 0 or len(self.config.password) == 0 or len(self.config.organizationID) == 0 or len(self.config.appID) == 0:
			raise Exception("Config missing")

	def __loginHeaders(self):
		result = self.basicHeaders
		return result

	def __urlEndPoint(self,path):
  		return 'https://www.fabric.io/api/v2/organizations/' + self.config.organizationID + '/apps/' + self.config.appID + '/' + path

  	def __dashboardHeaders(self):
		result = self.basicHeaders
		return result

	def __getDeveloperToken(self):
		request = urllib2.Request("https://fabric.io/api/v2/client_boot/config_data", headers=self.__loginHeaders())
		response = urllib2.urlopen(request)
		dic = json.loads(response.read())
		return dic['developer_token']

	def __getCRSFTokenAndSession(self):
		request = urllib2.Request('https://fabric.io/login')
		response = urllib2.urlopen(request)
		source = response.read()
		return {"csrf": self.__parseCRSF(source), 'session': self.__parseSession(response)}

	def __parseCRSF(self,raw):
		metaStartString = '<meta content="authenticity_token" name="csrf-param" />'
		metaEndString = 'name="csrf-token"'

		start = raw.find('<meta content="authenticity_token" name="csrf-param" />')
		end = raw.find('name="csrf-token"')
		meta = raw[start + len('<meta content="authenticity_token" name="csrf-param" />'):end]

		start = meta.find('<meta content="')
		csrf = meta[start + len('<meta content="'):]
		token = csrf.split('"')[0]
		return token

	def __parseSession(self,raw):
		cookie = raw.headers['Set-Cookie']
		start = cookie.find('_fabric_session=')
		meta = cookie[start + len('_fabric_session='):]
		session = meta.split(';')[0]
		return session

	def login(self):
		auth = self.__getCRSFTokenAndSession()
		token = self.__getDeveloperToken()
		self.basicHeaders['X-CSRF-Token'] = auth["csrf"]
		self.basicHeaders['X-CRASHLYTICS-DEVELOPER-TOKEN'] = token


		self.basicHeaders['Cookie'] = 'G_ENABLED_IDPS=google; _ga=GA1.2.1935437631.1526263142; _gid=GA1.2.874601089.1526263142; ' + '_fabric_session=' + auth["session"] + ';'
		post = 'email=' + self.config.email + '&' + 'password=' + self.config.password
		request = urllib2.Request("https://fabric.io/api/v2/session", post, self.__loginHeaders())
		response = urllib2.urlopen(request)

		newSession = self.__parseSession(response)
		self.basicHeaders['Cookie'] = 'G_ENABLED_IDPS=google; _ga=GA1.2.1935437631.1526263142; _gid=GA1.2.874601089.1526263142; ' + '_fabric_session=' + newSession + ';'
	  
	def topBuilds(self):
		url = self.__urlEndPoint('growth_analytics/top_builds.json?start=' + str(self.start) + '&end=' + str(self.end) + '&limit=4&show_launch_status=true')
		request = urllib2.Request(url, headers=self.__dashboardHeaders())
		response = urllib2.urlopen(request)
		dic = json.loads(response.read())
		return dic

	def buildDAU(self,para):
		url = self.__urlEndPoint('growth_analytics/multi_build_dau.json?start=' + str(self.start) + '&end=' + str(self.end) + '&builds=' + para)
		request = urllib2.Request(url, headers=self.__dashboardHeaders())
		response = urllib2.urlopen(request)
		dic = json.loads(response.read())
		return dic

	def buildCrashFreeUser(self):
		url = self.__urlEndPoint('growth_analytics/crash_free_users_for_top_builds.json?transformation=weighted&limit=3&start=' + str(self.start) +'&end=' + str(self.end))
		request = urllib2.Request(url, headers=self.__dashboardHeaders())
		response = urllib2.urlopen(request)
		dic = json.loads(response.read())
		return dic
