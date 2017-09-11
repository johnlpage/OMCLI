#!/usr/bin/python
import requests
from requests.auth import HTTPDigestAuth
import json
from urllib import quote_plus,quote
from pprint import pprint
import sys, getopt
import hashlib
import struct
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


#This to come from reading a secured local file

user = None
omhost = 'https://mongo-ops-man.bob.co.uk:8080'
baseurl = omhost + '/api/public/v1.0'
key = None
hostname = None
hostport = 27017
mongouser = None
mongopass = None
autoconfigfile = None
name = None
actions = ['create','show','import']
nouns = ['group','groups','user','host',"automation"]

def print_usage_message():
   print "usage: " + sys.argv[0] + " action object  [-h,--help] [-n,--name Name] [-u,--user OpsMgrUser] [-k,--keyfile file] [-c, --host] [-i, --mongouser] [-f, --automationconfig] "
   print "actions:\n\t"+str(actions)+" "+str(nouns)+"\n"

def parse_args(argv):
   global name
   global user
   global key
   global hostname
   global hostport
   global autoconfigfile
   global baseurl
   keyfile = None

   try:
      opts, args = getopt.getopt(argv,"n:u:k:c:i:f:m:h",["name=","user=","keyfile=","host=","mongouser=","automationconfig=","opsmgr=","help"])
   except getopt.GetoptError:
      print_usage_message()
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print_usage_message()
         print "arguments:"
         print '\n\t-n name\n\t-h Display help\n'
         sys.exit()
      elif opt in ("-n", "--name"):
         name = arg
      elif opt in ("-u", "--user"):
         user = arg
      elif opt in ("-k", "--keyfile"):
         keyfile = arg
      elif opt in ("-f", "--automationconfig"):
         autoconfigfile = arg
      elif opt in ("-m", "--opsmgr"):
         omhost = arg
         baseurl = omhost + '/api/public/v1.0'
      elif opt in ("-c", "--host"):
         parts = arg.split(':')
         hostname = parts[0]
         if len(parts)>1:
            hostport = parts[1]
      elif opt in ("-i", "--mongouser"):
         parts = arg.split('/')
         mongouser = parts[0]
         if len(parts)>1:
            mongopass = parts[1]


   if user == None or keyfile == None:
      print "User and KeyFile need to be specified with -u and -k"
      sys.exit(2)
   with open(keyfile,"r") as inkeyfile:
      key = inkeyfile.readline().rstrip()

def group_id_from_name(groupname):
   if groupname == None:
      print "You need to specify a Name for the group"
      sys.exit(2)

   url = baseurl+'/groups/byName/'+quote_plus(groupname)
   grouprequest = requests.get(url, auth=HTTPDigestAuth(user, key),verify=False)
   if grouprequest.status_code != 200:
      rval = grouprequest.json()
      print(rval.get('detail'))
      sys.exit(2)

   groupdata = grouprequest.json()
   mmsgroupid = groupdata.get('id')
   return mmsgroupid

def group_name_from_id(groupid):
   if groupid == None:
      return None

   url = baseurl+'/groups/'+groupid
   grouprequest = requests.get(url, auth=HTTPDigestAuth(user, key),verify=False)
   if grouprequest.status_code != 200:
      return None

   groupdata = grouprequest.json()
   return groupdata['name']


#Create a new Ops Manager Group
def create_group(argv):
   parse_args(argv)
   if name == None:
      print "You need to specify a group name"
      sys.exit(2)
   groupdoc = { 'name' : name }
 
   url = baseurl + '/groups'
   jsontxt = json.dumps(groupdoc)
 
   newgroupreq = requests.post(url, auth=HTTPDigestAuth(user, key), data = jsontxt, headers = { 'Content-Type' : 'application/json'},verify=False)
   if newgroupreq.status_code != 201:
      print "Error " + str(newgroupreq.status_code) 
      pprint(newgroupreq.json())
      sys.exit(2)
   data = newgroupreq.json()
   apikey = data['agentApiKey']
   print '{ "agentApiKey" : "' + apikey + '" }'
   print "WRITING API KEY TO LOCAL FILE !!!"
   f = open(str(name)+".agent.key", 'w')
   f.write('{ "agentApiKey" : "' + apikey + '" }')
   f.close()


def symname(thing):
   adjectives = ["abandoned","able","absolute","adorable","adventurous","academic","acceptable","acclaimed","accomplished","accurate","aching","acidic","acrobatic","active","actual","adept","admirable","admired","adolescent","adorable","adored","advanced","afraid","affectionate","aged","aggravating","aggressive","agile","agitated","agonizing","agreeable","ajar","alarmed","alarming","alert","alienated","alive","altruistic","amazing","ambitious","ample","amused","amusing","anchored","ancient","angelic","angry","anguished","animated","annual","another","antique","anxious","apprehensive","appropriate","arctic","arid","aromatic","artistic","ashamed","assured","astonishing","athletic","attached","attentive","attractive","austere","authentic","authorized","automatic","avaricious","average","aware","awesome","awful","awkward","babyish","back","baggy","bare","barren","basic","beautiful","belated","beloved","beneficial","better","best","bewitched","big-hearted","biodegradable","bite-sized","bitter","black","black-and-white","bland","blank","blaring","bleak","blind","blissful","blond","blue","blushing","bogus","boiling","bold","bony","boring","bossy","both","bouncy","bountiful","bowed","brave","breakable","brief","bright","brilliant","brisk","broken","bronze","brown","bruised","bubbly","bulky","bumpy","buoyant","burdensome","burly","bustling","busy","buttery","buzzing","calculating","calm","candid","canine","capital","carefree","careful","careless","caring","cautious","cavernous","celebrated","charming","cheap","cheerful","cheery","chief","chilly","chubby","circular","classic","clean","clear","clear-cut","clever","close","closed","cloudy","clueless","clumsy","cluttered","coarse","cold","colorful","colorless","colossal","comfortable","common","compassionate","competent","complete","complex","complicated","composed","concerned","concrete","confused","conscious","considerate","constant","content","conventional","cooked","cool","cooperative","coordinated","corny","corrupt","costly","courageous","courteous","crafty","crazy","creamy","creative","creepy","criminal","crisp","critical","crooked","crowded","cruel","crushing","cuddly","cultivated","cultured","cumbersome","curly","curvy","cute","cylindrical","damaged","damp","dangerous","dapper","daring","darling","dark","dazzling","dead","deadly","deafening","dear","dearest","decent","decimal","decisive","deep","defenseless","defensive","defiant","deficient","definite","definitive","delayed","delectable","delicious","delightful","delirious","demanding","dense","dental","dependable","dependent","descriptive","deserted","detailed","determined","devoted","different","difficult","digital","diligent","dimpled","dimwitted","direct","disastrous","discrete","disfigured","disgusting","disloyal","dismal","distant","downright","dreary","dirty","disguised","dishonest","dismal","distant","distinct","distorted","dizzy","dopey","doting","double","downright","drab","drafty","dramatic","dreary","droopy","dual","dull","dutiful","each","eager","earnest","early","easy","easy-going","ecstatic","edible","educated","elaborate","elastic","elated","elderly","electric","elegant","elementary","elliptical","embarrassed","embellished","eminent","emotional","empty","enchanted","enchanting","energetic","enlightened","enormous","enraged","entire","envious","equal","equatorial","essential","esteemed","ethical","euphoric","even","evergreen","everlasting","every","evil","exalted","excellent","exemplary","exhausted","excitable","excited","exciting","exotic","expensive","experienced","expert","extraneous","extroverted","extra-large","extra-small","fabulous","failing","faint","fair","faithful","fake","false","familiar","famous","fancy","fantastic","faraway","far-flung","far-off","fast","fatal","fatherly","favorable","favorite","fearful","fearless","feisty","feline","female","feminine","fickle","filthy","fine","finished","firm","first","firsthand","fitting","fixed","flaky","flamboyant","flashy","flat","flawed","flawless","flickering","flimsy","flippant","flowery","fluffy","fluid","flustered","focused","fond","foolhardy","foolish","forceful","forked","formal","forsaken","forthright","fortunate","fragrant","frail","frank","frayed","free","French","fresh","frequent","friendly","frightened","frightening","frigid","frilly","frizzy","frivolous","front","frosty","frozen","frugal","fruitful","full","fumbling","functional","funny","fussy","fuzzy","gargantuan","gaseous","general","generous","gentle","genuine","giant","giddy","gigantic","gifted","giving","glamorous","glaring","glass","gleaming","gleeful","glistening","glittering","gloomy","glorious","glossy","glum","golden","good","good-natured","gorgeous","graceful","gracious","grand","grandiose","granular","grateful","grave","gray","great","greedy","green","gregarious","grim","grimy","gripping","grizzled","gross","grotesque","grouchy","grounded","growing","growling","grown","grubby","gruesome","grumpy","guilty","gullible","gummy","hairy","half","handmade","handsome","handy","happy","happy-go-lucky","hard","hard-to-find","harmful","harmless","harmonious","harsh","hasty","hateful","haunting","healthy","heartfelt","hearty","heavenly","heavy","hefty","helpful","helpless","hidden","hideous","high","high-level","hilarious","hoarse","hollow","homely","honest","honorable","honored","hopeful","horrible","hospitable","huge","humble","humiliating","humming","humongous","hungry","hurtful","husky","icky","ideal","idealistic","identical","idle","idiotic","idolized","ignorant","illegal","ill-fated","ill-informed","illiterate","illustrious","imaginary","imaginative","immaculate","immaterial","immediate","immense","impassioned","impeccable","impartial","imperfect","imperturbable","impish","impolite","important","impossible","impractical","impressionable","impressive","improbable","impure","inborn","incomparable","incompatible","incomplete","inconsequential","incredible","indelible","inexperienced","indolent","infamous","infantile","infatuated","inferior","infinite","informal","innocent","insecure","insidious","insignificant","insistent","instructive","insubstantial","intelligent","intent","intentional","interesting","internal","international","intrepid","ironclad","irresponsible","irritating","itchy","jaded","jagged","jam-packed","jaunty","jealous","jittery","joint","jolly","jovial","joyful","joyous","jubilant","judicious","juicy","jumbo","junior","jumpy","juvenile","kaleidoscopic","keen","kind","kindhearted","kindly","klutzy","knobby","knotty","knowledgeable","knowing","known","kooky","kosher","lame","lanky","large","last","lasting","late","lavish","lawful","lazy","leading","lean","leafy","left","legal","legitimate","light","lighthearted","likable","likely","limited","limp","limping","linear","lined","liquid","little","live","lively","livid","loathsome","lone","lonely","long","long-term","loose","lopsided","lost","loud","lovable","lovely","loving","loyal","lucky","lumbering","luminous","lumpy","lustrous","luxurious","made-up","magnificent","majestic","major","male","mammoth","married","marvelous","masculine","massive","mature","meager","mealy","mean","measly","meaty","medical","mediocre","medium","meek","mellow","melodic","memorable","menacing","merry","messy","metallic","mild","milky","mindless","miniature","minor","minty","miserable","miserly","misguided","misty","mixed","modern","modest","moist","monstrous","monthly","monumental","moral","mortified","motherly","motionless","mountainous","muddy","muffled","multicolored","mundane","murky","mushy","musty","muted","mysterious","naive","narrow","nasty","natural","naughty","nautical","near","neat","necessary","needy","negative","neglected","negligible","neighboring","nervous","next","nice","nifty","nimble","nippy","nocturnal","noisy","nonstop","normal","notable","noted","noteworthy","novel","noxious","numb","nutritious","nutty","obedient","obese","oblong","oily","oblong","obvious","occasional","oddball","offbeat","offensive","official","old-fashioned","only","open","optimal","optimistic","opulent","orange","orderly","organic","ornate","ornery","ordinary","original","other","outlying","outgoing","outlandish","outrageous","outstanding","oval","overcooked","overdue","overjoyed","overlooked","palatable","pale","paltry","parallel","parched","partial","passionate","past","pastel","peaceful","peppery","perfect","perfumed","periodic","perky","personal","pertinent","pesky","pessimistic","petty","phony","physical","piercing","pink","pitiful","plain","plaintive","plastic","playful","pleasant","pleased","pleasing","plump","plush","polished","polite","political","pointed","pointless","poised","poor","popular","portly","posh","positive","possible","potable","powerful","powerless","practical","precious","present","prestigious","pretty","precious","previous","pricey","prickly","primary","prime","pristine","private","prize","probable","productive","profitable","profuse","proper","proud","prudent","punctual","pungent","puny","pure","purple","pushy","putrid","puzzled","puzzling","quaint","qualified","quarrelsome","quarterly","queasy","querulous","questionable","quick","quick-witted","quiet","quintessential","quirky","quixotic","quizzical","radiant","ragged","rapid","rare","rash","recent","reckless","rectangular","ready","real","realistic","reasonable","reflecting","regal","regular","reliable","relieved","remarkable","remorseful","remote","repentant","required","respectful","responsible","repulsive","revolving","rewarding","rich","rigid","right","ringed","ripe","roasted","robust","rosy","rotating","rotten","rough","round","rowdy","royal","rubbery","rundown","ruddy","rude","runny","rural","rusty","safe","salty","same","sandy","sane","sarcastic","sardonic","satisfied","scaly","scarce","scared","scary","scented","scholarly","scientific","scornful","scratchy","scrawny","second","secondary","second-hand","secret","self-assured","self-reliant","selfish","sentimental","separate","serene","serious","serpentine","several","severe","shabby","shadowy","shady","shallow","shameful","shameless","sharp","shimmering","shiny","shocked","shocking","shoddy","short","short-term","showy","shrill","sick","silent","silky","silly","silver","similar","simple","simplistic","sinful","single","sizzling","skeletal","skinny","sleepy","slight","slim","slimy","slippery","slow","slushy","small","smart","smoggy","smooth","smug","snappy","snarling","sneaky","sniveling","snoopy","sociable","soft","soggy","solid","somber","some","spherical","sophisticated","sore","sorrowful","soulful","soupy","sour","Spanish","sparkling","sparse","specific","spectacular","speedy","spicy","spiffy","spirited","spiteful","splendid","spotless","spotted","spry","square","squeaky","squiggly","stable","staid","stained","stale","standard","starchy","stark","starry","steep","sticky","stiff","stimulating","stingy","stormy","straight","strange","steel","strict","strident","striking","striped","strong","studious","stunning","stupendous","stupid","sturdy","stylish","subdued","submissive","substantial","subtle","suburban","sudden","sugary","sunny","super","superb","superficial","superior","supportive","sure-footed","surprised","suspicious","svelte","sweaty","sweet","sweltering","swift","sympathetic","tall","talkative","tame","tangible","tart","tasty","tattered","taut","tedious","teeming","tempting","tender","tense","tepid","terrible","terrific","testy","thankful","that","these","thick","thin","third","thirsty","this","thorough","thorny","those","thoughtful","threadbare","thrifty","thunderous","tidy","tight","timely","tinted","tiny","tired","torn","total","tough","traumatic","treasured","tremendous","tragic","trained","tremendous","triangular","tricky","trifling","trim","trivial","troubled","true","trusting","trustworthy","trusty","truthful","tubby","turbulent","twin","ugly","ultimate","unacceptable","unaware","uncomfortable","uncommon","unconscious","understated","unequaled","uneven","unfinished","unfit","unfolded","unfortunate","unhappy","unhealthy","uniform","unimportant","unique","united","unkempt","unknown","unlawful","unlined","unlucky","unnatural","unpleasant","unrealistic","unripe","unruly","unselfish","unsightly","unsteady","unsung","untidy","untimely","untried","untrue","unused","unusual","unwelcome","unwieldy","unwilling","unwitting","unwritten","upbeat","upright","upset","urban","usable","used","useful","useless","utilized","utter","vacant","vague","vain","valid","valuable","vapid","variable","vast","velvety","venerated","vengeful","verifiable","vibrant","vicious","victorious","vigilant","vigorous","villainous","violet","violent","virtual","virtuous","visible","vital","vivacious","vivid","voluminous","warlike","warm","warmhearted","warped","wary","wasteful","watchful","waterlogged","watery","wavy","wealthy","weak","weary","webbed","weekly","weepy","weighty","weird","welcome","well-documented","well-groomed","well-informed","well-lit","well-made","well-off","well-to-do","well-worn","which","whimsical","whirlwind","whispered","white","whole","whopping","wicked","wide","wide-eyed","wiggly","wild","willing","wilted","winding","windy","winged","wiry","wise","witty","wobbly","woeful","wonderful","wooden","woozy","wordy","worldly","worn","worried","worrisome","worse","worst","worthless","worthwhile","worthy","wrathful","wretched","writhing","wrong","yawning","yearly","yellow","yellowish","young","youthful","yummy","zany","zealous","zesty","zigzag"]
   nouns=["people","history","way","art","world","information","map","two","family","government","health","system","computer","meat","year","thanks","music","person","reading","method","data","food","understanding","theory","law","bird","literature","problem","software","control","knowledge","power","ability","economics","love","internet","television","science","library","nature","fact","product","idea","temperature","investment","area","society","activity","story","industry","media","thing","oven","community","definition","safety","quality","development","language","management","player","variety","video","week","security","country","exam","movie","organization","equipment","physics","analysis","policy","series","thought","basis","boyfriend","direction","strategy","technology","army","camera","freedom","paper","environment","child","instance","month","truth","marketing","university","writing","article","department","difference","goal","news","audience","fishing","growth","income","marriage","user","combination","failure","meaning","medicine","philosophy","teacher","communication","night","chemistry","disease","disk","energy","nation","road","role","soup","advertising","location","success","addition","apartment","education","math","moment","painting","politics","attention","decision","event","property","shopping","student","wood","competition","distribution","entertainment","office","population","president","unit","category","cigarette","context","introduction","opportunity","performance","driver","flight","length","magazine","newspaper","relationship","teaching","cell","dealer","finding","lake","member","message","phone","scene","appearance","association","concept","customer","death","discussion","housing","inflation","insurance","mood","woman","advice","blood","effort","expression","importance","opinion","payment","reality","responsibility","situation","skill","statement","wealth","application","city","county","depth","estate","foundation","grandmother","heart","perspective","photo","recipe","studio","topic","collection","depression","imagination","passion","percentage","resource","setting","ad","agency","college","connection","criticism","debt","description","memory","patience","secretary","solution","administration","aspect","attitude","director","personality","psychology","recommendation","response","selection","storage","version","alcohol","argument","complaint","contract","emphasis","highway","loss","membership","possession","preparation","steak","union","agreement","cancer","currency","employment","engineering","entry","interaction","mixture","preference","region","republic","tradition","virus","actor","classroom","delivery","device","difficulty","drama","election","engine","football","guidance","hotel","owner","priority","protection","suggestion","tension","variation","anxiety","atmosphere","awareness","bath","bread","candidate","climate","comparison","confusion","construction","elevator","emotion","employee","employer","guest","height","leadership","mall","manager","operation","recording","sample","transportation","charity","cousin","disaster","editor","efficiency","excitement","extent","feedback","guitar","homework","leader","mom","outcome","permission","presentation","promotion","reflection","refrigerator","resolution","revenue","session","singer","tennis","basket","bonus","cabinet","childhood","church","clothes","coffee","dinner","drawing","hair","hearing","initiative","judgment","lab","measurement","mode","mud","orange","poetry","police","possibility","procedure","queen","ratio","relation","restaurant","satisfaction","sector","signature","significance","song","tooth","town","vehicle","volume","wife","accident","airport","appointment","arrival","assumption","baseball","chapter","committee","conversation","database","enthusiasm","error","explanation","farmer","gate","girl","hall","historian","hospital","injury","instruction","maintenance","manufacturer","meal","perception","pie","poem","presence","proposal","reception","replacement","revolution","river","son","speech","tea","village","warning","winner","worker","writer","assistance","breath","buyer","chest","chocolate","conclusion","contribution","cookie","courage","dad","desk","drawer","establishment","examination","garbage","grocery","honey","impression","improvement","independence","insect","inspection","inspector","king","ladder","menu","penalty","piano","potato","profession","professor","quantity","reaction","requirement","salad","sister","supermarket","tongue","weakness","wedding","affair","ambition","analyst","apple","assignment","assistant","bathroom","bedroom","beer","birthday","celebration","championship","cheek","client","consequence","departure","diamond","dirt","ear","fortune","friendship","funeral","gene","girlfriend","hat","indication","intention","lady","midnight","negotiation","obligation","passenger","pizza","platform","poet","pollution","recognition","reputation","shirt","sir","speaker","stranger","surgery","sympathy","tale","throat","trainer","uncle","youth","time","work","film","water","money","example","while","business","study","game","life","form","air","day","place","number","part","field","fish","back","process","heat","hand","experience","job","book","end","point","type","home","economy","value","body","market","guide","interest","state","radio","course","company","price","size","card","list","mind","trade","line","care","group","risk","word","fat","force","key","light","training","name","school","top","amount","level","order","practice","research","sense","service","piece","web","boss","sport","fun","house","page","term","test","answer","sound","focus","matter","kind","soil","board","oil","picture","access","garden","range","rate","reason","future","site","demand","exercise","image","case","cause","coast","action","age","bad","boat","record","result","section","building","mouse","cash","class","nothing","period","plan","store","tax","side","subject","space","rule","stock","weather","chance","figure","man","model","source","beginning","earth","program","chicken","design","feature","head","material","purpose","question","rock","salt","act","birth","car","dog","object","scale","sun","note","profit","rent","speed","style","war","bank","craft","half","inside","outside","standard","bus","exchange","eye","fire","position","pressure","stress","advantage","benefit","box","frame","issue","step","cycle","face","item","metal","paint","review","room","screen","structure","view","account","ball","discipline","medium","share","balance","bit","black","bottom","choice","gift","impact","machine","shape","tool","wind","address","average","career","culture","morning","pot","sign","table","task","condition","contact","credit","egg","hope","ice","network","north","square","attempt","date","effect","link","post","star","voice","capital","challenge","friend","self","shot","brush","couple","debate","exit","front","function","lack","living","plant","plastic","spot","summer","taste","theme","track","wing","brain","button","click","desire","foot","gas","influence","notice","rain","wall","base","damage","distance","feeling","pair","savings","staff","sugar","target","text","animal","author","budget","discount","file","ground","lesson","minute","officer","phase","reference","register","sky","stage","stick","title","trouble","bowl","bridge","campaign","character","club","edge","evidence","fan","letter","lock","maximum","novel","option","pack","park","plenty","quarter","skin","sort","weight","baby","background","carry","dish","factor","fruit","glass","joint","master","muscle","red","strength","traffic","trip","vegetable","appeal","chart","gear","ideal","kitchen","land","log","mother","net","party","principle","relative","sale","season","signal","spirit","street","tree","wave","belt","bench","commission","copy","drop","minimum","path","progress","project","sea","south","status","stuff","ticket","tour","angle","blue","breakfast","confidence","daughter","degree","doctor","dot","dream","duty","essay","father","fee","finance","hour","juice","limit","luck","milk","mouth","peace","pipe","seat","stable","storm","substance","team","trick","afternoon","bat","beach","blank","catch","chain","consideration","cream","crew","detail","gold","interview","kid","mark","match","mission","pain","pleasure","score","screw","sex","shop","shower","suit","tone","window","agent","band","block","bone","calendar","cap","coat","contest","corner","court","cup","district","door","east","finger","garage","guarantee","hole","hook","implement","layer","lecture","lie","manner","meeting","nose","parking","partner","profile","respect","rice","routine","schedule","swimming","telephone","tip","winter","airline","bag","battle","bed","bill","bother","cake","code","curve","designer","dimension","dress","ease","emergency","evening","extension","farm","fight","gap","grade","holiday","horror","horse","host","husband","loan","mistake","mountain","nail","noise","occasion","package","patient","pause","phrase","proof","race","relief","sand","sentence","shoulder","smoke","stomach","string","tourist","towel","vacation","west","wheel","wine","arm","aside","associate","bet","blow","border","branch","breast","brother","buddy","bunch","chip","coach","cross","document","draft","dust","expert","floor","god","golf","habit","iron","judge","knife","landscape","league","mail","mess","native","opening","parent","pattern","pin","pool","pound","request","salary","shame","shelter","shoe","silver","tackle","tank","trust","assist","bake","bar","bell","bike","blame","boy","brick","chair","closet","clue","collar","comment","conference","devil","diet","fear","fuel","glove","jacket","lunch","monitor","mortgage","nurse","pace","panic","peak","plane","reward","row","sandwich","shock","spite","spray","surprise","till","transition","weekend","welcome","yard","alarm","bend","bicycle","bite","blind","bottle","cable","candle","clerk","cloud","concert","counter","flower","grandfather","harm","knee","lawyer","leather","load","mirror","neck","pension","plate","purple","ruin","ship","skirt","slice","snow","specialist","stroke","switch","trash","tune","zone","anger","award","bid","bitter","boot","bug","camp","candy","carpet","cat","champion","channel","clock","comfort","cow","crack","engineer","entrance","fault","grass","guy","hell","highlight","incident","island","joke","jury","leg","lip","mate","motor","nerve","passage","pen","pride","priest","prize","promise","resident","resort","ring","roof","rope","sail","scheme","script","sock","station","toe","tower","truck","witness","a","you","it","can","will","if","one","many","most","other","use","make","good","look","help","go","great","being","few","might","still","public","read","keep","start","give","human","local","general","she","specific","long","play","feel","high","tonight","put","common","set","change","simple","past","big","possible","particular","today","major","personal","current","national","cut","natural","physical","show","try","check","second","call","move","pay","let","increase","single","individual","turn","ask","buy","guard","hold","main","offer","potential","professional","international","travel","cook","alternative","following","special","working","whole","dance","excuse","cold","commercial","low","purchase","deal","primary","worth","fall","necessary","positive","produce","search","present","spend","talk","creative","tell","cost","drive","green","support","glad","remove","return","run","complex","due","effective","middle","regular","reserve","independent","leave","original","reach","rest","serve","watch","beautiful","charge","active","break","negative","safe","stay","visit","visual","affect","cover","report","rise","walk","white","beyond","junior","pick","unique","anything","classic","final","lift","mix","private","stop","teach","western","concern","familiar","fly","official","broad","comfortable","gain","maybe","rich","save","stand","young","fail","heavy","hello","lead","listen","valuable","worry","handle","leading","meet","release","sell","finish","normal","press","ride","secret","spread","spring","tough","wait","brown","deep","display","flow","hit","objective","shoot","touch","cancel","chemical","cry","dump","extreme","push","conflict","eat","fill","formal","jump","kick","opposite","pass","pitch","remote","total","treat","vast","abuse","beat","burn","deposit","print","raise","sleep","somewhere","advance","anywhere","consist","dark","double","draw","equal","fix","hire","internal","join","kill","sensitive","tap","win","attack","claim","constant","drag","drink","guess","minor","pull","raw","soft","solid","wear","weird","wonder","annual","count","dead","doubt","feed","forever","impress","nobody","repeat","round","sing","slide","strip","whereas","wish","combine","command","dig","divide","equivalent","hang","hunt","initial","march","mention","smell","spiritual","survey","tie","adult","brief","crazy","escape","gather","hate","prior","repair","rough","sad","scratch","sick","strike","employ","external","hurt","illegal","laugh","lay","mobile","nasty","ordinary","respond","royal","senior","split","strain","struggle","swim","train","upper","wash","yellow","convert","crash","dependent","fold","funny","grab","hide","miss","permit","quote","recover","resolve","roll","sink","slip","spare","suspect","sweet","swing","twist","upstairs","usual","abroad","brave","calm","concentrate","estimate","grand","male","mine","prompt","quiet","refuse","regret","reveal","rush","shake","shift","shine","steal","suck","surround","anybody","bear","brilliant","dare","dear","delay","drunk","female","hurry","inevitable","invite","kiss","neat","pop","punch","quit","reply","representative","resist","rip","rub","silly","smile","spell","stretch","stupid","tear","temporary","tomorrow","wake","wrap","yesterday"]
   nnouns = len(nouns)
   nadj = len(adjectives)
   dig = hashlib.md5(str(thing)).digest()
   digint = struct.unpack("<L",dig[0:4])[0]
   adjv = digint % nadj
   digint = struct.unpack("<L",dig[4:8])[0]
   nounv = digint % nnouns
   return adjectives[adjv]+"_"+nouns[nounv]


def show_user(argv):
   parse_args(argv)
   url = baseurl + '/users/byName/'+quote(user)
   print user + "=" + key
   print url
   autconfrequest = requests.get(url, auth=HTTPDigestAuth(user, key),verify=False)
   if autconfrequest.status_code != 200:
      pprint(autconfrequest.json())
      sys.exit(2)
   rObj = autconfrequest.json()
   #delattr(rObj,'links')
   rObj['_handle']=symname(rObj['id'])
   del rObj['links']
   del rObj['roles']

   print(json.dumps(rObj,sort_keys=True,indent=4, separators=(',', ': ')))

def show_user_groups(argv):
   parse_args(argv)
   url = baseurl + '/users/byName/'+quote(user)
   autconfrequest = requests.get(url, auth=HTTPDigestAuth(user, key),verify=False)
   if autconfrequest.status_code != 200:
      pprint(autconfrequest.json())
      sys.exit(2)
   jsonObj = autconfrequest.json()
   roleList = jsonObj.get('roles')
   groups = []
   for role in roleList:
      gID = role.get('groupId',None)
      if gID != None:
         gHandle = symname(gID)
         gName = group_name_from_id(gID)
         if gName != None:
            groups.append({'_handle':gHandle,'name':gName,'id':gID,'role':role.get('roleName')})
   print(json.dumps(groups,sort_keys=True,indent=4, separators=(',', ': ')))

def show_group(argv):
   parse_args(argv)
   if name == None:
      print "You need to specify a group name"
      sys.exit(2)

   url = baseurl+'/groups/byName/'+quote_plus(name)
   grouprequest = requests.get(url, auth=HTTPDigestAuth(user, key),verify=False)
   if grouprequest.status_code != 200:
      pprint(grouprequest.json())
      sys.exit(2)
   r = grouprequest.json()
   r['links']=None
   print(json.dumps(r,sort_keys=True,indent=4, separators=(',', ': ')))

def import_host(argv):
   parse_args(argv)
   if name == None:
      print "You need to specify a group name to import this host to"
      sys.exit(2)

   if hostname == None:
      print "You need to specify the hostname to import"
      sys.exit(2)

   groupid = group_id_from_name(name)

   url = baseurl + "/groups/" + groupid + "/hosts"
   newhostdoc = { 'hostname' : hostname, 'port': hostport }
   if mongouser != None:
      newhostdoc['username'] = mongouser
      newhostdoc['password'] = mongopass


   jsontxt = json.dumps(newhostdoc)
 
   newhostreq = requests.post(url, auth=HTTPDigestAuth(user, key), data = jsontxt, headers = { 'Content-Type' : 'application/json'},verify=False)
   if newhostreq.status_code != 201:
      print "Error " + str(newhostreq.status_code) 
      pprint(newhostreq.json())
      sys.exit(2)
   data = newhostreq.json()
   print(json.dumps(data,sort_keys=True,indent=4, separators=(',', ': ')))



def import_automation(argv):
   parse_args(argv)
   if name == None:
      print "You need to specify a group name to import this host to"
      sys.exit(2)

   if autoconfigfile == None:
      print "You need to specify a file with the automation config"
      sys.exit(2)

   groupid = group_id_from_name(name)

   with open(autoconfigfile,"r") as autoconffile:
      content = autoconffile.read()

   url = baseurl + "/groups/" + groupid + "/automationConfig"
   print "Calling " + url
   newhostreq = requests.put(url, auth=HTTPDigestAuth(user, key), data = content, headers = { 'Content-Type' : 'application/json'},verify=False)
   if newhostreq.status_code != 200:
      print "Error " + str(newhostreq.status_code) 
      pprint(newhostreq.json())
      sys.exit(2)
   #Now poll until it's done or breaks

   infourl = baseurl + "/groups/" + groupid + "/automationStatus"
   done = False
   while done == False:
      time.sleep(3)
      statusrequest = requests.get(infourl, auth=HTTPDigestAuth(user, key),verify=False)
      if statusrequest.status_code != 200:
         pprint(statusrequest.json())
         sys.exit(2)
      data = statusrequest.json()
      print(json.dumps(data,sort_keys=True,indent=4, separators=(',', ': ')))
      done = True
      goal = data['goalVersion']
      for p in data['processes']:
         if p['lastGoalVersionAchieved'] != goal:
            done = False


def show_automation(argv):
   parse_args(argv)
   if name == None:
      print "You need to specify a group name to display automation for"
      sys.exit(2)

   groupid = group_id_from_name(name)


   url = baseurl + "/groups/" + groupid + "/automationConfig"
   statusrequest = requests.get(url, auth=HTTPDigestAuth(user, key),verify=False)
   if statusrequest.status_code != 200:
      pprint(statusrequest.json())
      sys.exit(2)
   data = statusrequest.json()
   print(json.dumps(data,sort_keys=True,indent=4, separators=(',', ': ')))


 

if __name__ == "__main__":
   if len(sys.argv) < 3:
      print_usage_message()
      sys.exit(1)
   
   actiontype = sys.argv[1]
   nountype = sys.argv[2]
   if actiontype == "show":
      if nountype == "user":
         show_user(sys.argv[3:])
         sys.exit()
      elif nountype == "groups":
         show_user_groups(sys.argv[3:])
         sys.exit()
      elif nountype == "group":
         show_group(sys.argv[3:])
         sys.exit()
      elif nountype == "automation":
         show_automation(sys.argv[3:])
         sys.exit()
      else:
         print "I don't know how to show " + nountype
         sys.exit(2)
   elif actiontype == "create":
      if nountype == "group":
         create_group(sys.argv[3:])
         sys.exit()
      else:
         print "I don't know how to create a " + nountype
         sys.exit(2)
   elif actiontype == "import":
      if nountype == "host":
         import_host(sys.argv[3:])
         sys.exit()
      if nountype == "automation":
         import_automation(sys.argv[3:])
         sys.exit()
      else:
         print "I don't know how to import a " + nountype
         sys.exit(2)
  
   print "Unknown operation '" + actiontype + "'"
   print_usage_message()
   sys.exit(1)


