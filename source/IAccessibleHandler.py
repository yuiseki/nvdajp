#IAccessibleHandler.py
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2006-2007 NVDA Contributors <http://www.nvda-project.org/>
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

#Constants
#IAccessible Object IDs
OBJID_WINDOW=0
OBJID_SYSMENU=-1
OBJID_TITLEBAR=-2
OBJID_MENU=-3
OBJID_CLIENT=-4
OBJID_VSCROLL=-5
OBJID_HSCROLL=-6
OBJID_SIZEGRIP=-7
OBJID_CARET=-8
OBJID_CURSOR=-9
OBJID_ALERT=-10
OBJID_SOUND=-11
OBJID_NATIVEOM=-16
#IAccessible navigation
NAVDIR_DOWN=2
NAVDIR_FIRSTCHILD=7
NAVDIR_LASTCHILD=8
NAVDIR_LEFT=3
NAVDIR_NEXT=5
NAVDIR_PREVIOUS=6
NAVDIR_RIGHT=4
NAVDIR_UP=1
#IAccessible roles
ROLE_SYSTEM_TITLEBAR=1
ROLE_SYSTEM_MENUBAR=2
ROLE_SYSTEM_SCROLLBAR=3
ROLE_SYSTEM_GRIP=4
ROLE_SYSTEM_SOUND=5
ROLE_SYSTEM_CURSOR=6
ROLE_SYSTEM_CARET=7
ROLE_SYSTEM_ALERT=8
ROLE_SYSTEM_WINDOW=9
ROLE_SYSTEM_CLIENT=10
ROLE_SYSTEM_MENUPOPUP=11
ROLE_SYSTEM_MENUITEM=12
ROLE_SYSTEM_TOOLTIP=13
ROLE_SYSTEM_APPLICATION=14
ROLE_SYSTEM_DOCUMENT=15
ROLE_SYSTEM_PANE=16
ROLE_SYSTEM_CHART=17
ROLE_SYSTEM_DIALOG=18
ROLE_SYSTEM_BORDER=19
ROLE_SYSTEM_GROUPING=20
ROLE_SYSTEM_SEPARATOR=21
ROLE_SYSTEM_TOOLBAR=22
ROLE_SYSTEM_STATUSBAR=23
ROLE_SYSTEM_TABLE=24
ROLE_SYSTEM_COLUMNHEADER=25
ROLE_SYSTEM_ROWHEADER=26
ROLE_SYSTEM_COLUMN=27
ROLE_SYSTEM_ROW=28
ROLE_SYSTEM_CELL=29
ROLE_SYSTEM_LINK=30
ROLE_SYSTEM_HELPBALLOON=31
ROLE_SYSTEM_CHARACTER=32
ROLE_SYSTEM_LIST=33
ROLE_SYSTEM_LISTITEM=34
ROLE_SYSTEM_OUTLINE=35
ROLE_SYSTEM_OUTLINEITEM=36
ROLE_SYSTEM_PAGETAB=37
ROLE_SYSTEM_PROPERTYPAGE=38
ROLE_SYSTEM_INDICATOR=39
ROLE_SYSTEM_GRAPHIC=40
ROLE_SYSTEM_STATICTEXT=41
ROLE_SYSTEM_TEXT=42
ROLE_SYSTEM_PUSHBUTTON=43
ROLE_SYSTEM_CHECKBUTTON=44
ROLE_SYSTEM_RADIOBUTTON=45
ROLE_SYSTEM_COMBOBOX=46
ROLE_SYSTEM_DROPLIST=47
ROLE_SYSTEM_PROGRESSBAR=48
ROLE_SYSTEM_DIAL=49
ROLE_SYSTEM_HOTKEYFIELD=50
ROLE_SYSTEM_SLIDER=51
ROLE_SYSTEM_SPINBUTTON=52
ROLE_SYSTEM_DIAGRAM=53
ROLE_SYSTEM_ANIMATION=54
ROLE_SYSTEM_EQUATION=55
ROLE_SYSTEM_BUTTONDROPDOWN=56
ROLE_SYSTEM_BUTTONMENU=57
ROLE_SYSTEM_BUTTONDROPDOWNGRID=58
ROLE_SYSTEM_WHITESPACE=59
ROLE_SYSTEM_PAGETABLIST=60
ROLE_SYSTEM_CLOCK=61
ROLE_SYSTEM_SPLITBUTTON=62
ROLE_SYSTEM_IPADDRESS=63
ROLE_SYSTEM_OUTLINEBUTTON=64
#IAccessible states
STATE_SYSTEM_UNAVAILABLE=0x1
STATE_SYSTEM_SELECTED=0x2
STATE_SYSTEM_FOCUSED=0x4
STATE_SYSTEM_PRESSED=0x8
STATE_SYSTEM_CHECKED=0x10
STATE_SYSTEM_MIXED=0x20
STATE_SYSTEM_READONLY=0x40
STATE_SYSTEM_HOTTRACKED=0x80
STATE_SYSTEM_DEFAULT=0x100
STATE_SYSTEM_EXPANDED=0x200
STATE_SYSTEM_COLLAPSED=0x400
STATE_SYSTEM_BUSY=0x800
STATE_SYSTEM_FLOATING=0x1000
STATE_SYSTEM_MARQUEED=0x2000
STATE_SYSTEM_ANIMATED=0x4000
STATE_SYSTEM_INVISIBLE=0x8000
STATE_SYSTEM_OFFSCREEN=0x10000
STATE_SYSTEM_SIZEABLE=0x20000
STATE_SYSTEM_MOVEABLE=0x40000
STATE_SYSTEM_SELFVOICING=0x80000
STATE_SYSTEM_FOCUSABLE=0x100000
STATE_SYSTEM_SELECTABLE=0x200000
STATE_SYSTEM_LINKED=0x400000
STATE_SYSTEM_TRAVERSED=0x800000
STATE_SYSTEM_MULTISELECTABLE=0x1000000
STATE_SYSTEM_EXTSELECTABLE=0x2000000
STATE_SYSTEM_HASSUBMENU=0x4000000
STATE_SYSTEM_ALERT_LOW=0x4000000
STATE_SYSTEM_ALERT_MEDIUM=0x8000000
STATE_SYSTEM_ALERT_HIGH=0x10000000
STATE_SYSTEM_PROTECTED=0x20000000
STATE_SYSTEM_HASPOPUP=0x40000000
STATE_SYSTEM_VALID=0x1fffffff

#Special Mozilla gecko MSAA constant additions
NAVRELATION_LABELLED_BY=0x1002
NAVRELATION_LABELLED_BY=0x1003

roleNames={
	ROLE_SYSTEM_CLIENT:_("window"),
	ROLE_SYSTEM_PAGETAB:_("tab"),
	ROLE_SYSTEM_TEXT:_("edit"),
	ROLE_SYSTEM_PUSHBUTTON:_("button"),
	ROLE_SYSTEM_OUTLINE:_("Tree view"),
}

stateNames={
	STATE_SYSTEM_HASPOPUP:_("sub menu"),
}

import tones
import ctypes
import comtypes.client
import comtypes.automation
import globalVars
import JABHandler
import eventHandler
import winUser
import speech
import api
import queueHandler
import virtualBuffers
import NVDAObjects.IAccessible
import appModuleHandler
import config
import IA2Handler
import mouseHandler
import controlTypes

#A list to store handles received from setWinEventHook, for use with unHookWinEvent  
objectEventHandles=[]

#Keep track of the last event
lastEventParams=None

#Load IAccessible from oleacc.dll
oleaccModule=comtypes.client.GetModule('oleacc.dll')
IAccessible=oleaccModule.IAccessible
IAccIdentity=oleaccModule.IAccIdentity
pointer_IAccessible=ctypes.POINTER(IAccessible)
oleAcc=ctypes.windll.oleacc

lastEvent=None

def getRoleName(role):
	if isinstance(role,int):
		return getRoleText(role)
	else:
		return role

def getStateNames(states,opposite=False):
	return " ".join([getStateName(state,opposite) for state in api.createStateList(states)])

def getStateName(state,opposite=False):
	if isinstance(state,int):
		newState=getStateText(state)
	else:
		newState=state
	if opposite:
		newState=_("not %s")%newState
	return newState

#A c ctypes struct to hold the x and y of a point on the screen 
class screenPointType(ctypes.Structure):
	_fields_=[
	('x',ctypes.c_int),
	('y',ctypes.c_int)
	]

def accessibleObjectFromWindow(window,objectID):
	if not winUser.isWindow(window):
		return None
	ptr=pointer_IAccessible()
	res=oleAcc.AccessibleObjectFromWindow(window,objectID,ctypes.byref(IAccessible._iid_),ctypes.byref(ptr))
	if res==0:
		return ptr
	else:
		return None

def accessibleObjectFromEvent(window,objectID,childID):
	if not winUser.isWindow(window):
		return None
	pacc=pointer_IAccessible()
	varChild=comtypes.automation.VARIANT()
	res=oleAcc.AccessibleObjectFromEvent(window,objectID,childID,ctypes.byref(pacc),ctypes.byref(varChild))
	if res==0:
		#speech.speakMessage("%s %s"%(childID,varChild.value))
		#if False or childID<0:
		#child=childID
		#else:
		child=varChild.value
		return (pacc,child)
	else:
		return None

def accessibleObjectFromPoint(x,y):
	point=screenPointType(x,y)
	pacc=pointer_IAccessible()
	varChild=comtypes.automation.VARIANT()
	res=oleAcc.AccessibleObjectFromPoint(point,ctypes.byref(pacc),ctypes.byref(varChild))
	if res==0:
		if not isinstance(varChild.value,int):
			child=0
		else:
			child=varChild.value
		return (pacc,child)

def windowFromAccessibleObject(ia):
	hwnd=ctypes.c_int()
	try:
		res=oleAcc.WindowFromAccessibleObject(ia,ctypes.byref(hwnd))
	except:
		res=0
	if res==0:
		return hwnd.value
	else:
		return 0

def accessibleChildren(ia,startIndex,numChildren):
	children=(comtypes.automation.VARIANT*numChildren)()
	realCount=ctypes.c_int()
	oleAcc.AccessibleChildren(ia,startIndex,numChildren,children,ctypes.byref(realCount))
	children=[x.value for x in children[0:realCount.value]]
	for childNum in xrange(len(children)):
		if isinstance(children[childNum],IAccessible):
			children[childNum]=(children[childNum],0)
		elif isinstance(children[childNum],comtypes.client.dynamic._Dispatch) or isinstance(children[childNum],comtypes.automation.IUnknown):
			children[childNum]=(children[childNum].QueryInterface(IAccessible),0)
		elif isinstance(children[childNum],int):
			children[childNum]=(ia,children[childNum])
	return children

def getRoleText(role):
	if roleNames.has_key(role):
		return roleNames[role]
	textLen=oleAcc.GetRoleTextW(role,0,0)
	if textLen:
		buf=ctypes.create_unicode_buffer(textLen+2)
		oleAcc.GetRoleTextW(role,buf,textLen+1)
		return buf.value
	else:
		return None

def getStateText(state):
	if stateNames.has_key(state):
		return stateNames[state]
	textLen=oleAcc.GetStateTextW(state,0,0)
	if textLen:
		buf=ctypes.create_unicode_buffer(textLen+2)
		oleAcc.GetStateTextW(state,buf,textLen+1)
		return buf.value
	else:
		return None

def accName(ia,child):
	try:
		return ia.accName(child)
	except:
		return ""

def accValue(ia,child):
	try:
		return ia.accValue(child)
	except:
		return ""

def accRole(ia,child):
	try:
		return ia.accRole(child)
	except:
		return 0

def accState(ia,child):
	try:
		return ia.accState(child)
	except:
		return 0

def accDescription(ia,child):
	try:
		return ia.accDescription(child)
	except:
		return ""

def accHelp(ia,child):
	try:
		return ia.accHelp(child)
	except:
		return ""

def accKeyboardShortcut(ia,child):
	try:
		return ia.accKeyboardShortcut(child)
	except:
		return ""

def accDoDefaultAction(ia,child):
	try:
		ia.accDoDefaultAction(child)
	except:
		pass

def accSelect(ia,child,flags):
		ia.accSelect(flags,child)

def accFocus(ia):
	try:
		res=ia.accFocus
		if isinstance(res,IAccessible):
			new_ia=res
			new_child=0
		elif isinstance(res,comtypes.client.dynamic._Dispatch) or isinstance(res,comtypes.automation.IUnknown):
			new_ia=res.QueryInterface(IAccessible)
			new_child=0
		elif isinstance(res,int):
			new_ia=ia
			new_child=res
		else:
			return None
		return (new_ia,new_child)
	except:
		return None

def accHitTest(ia,child,x,y):
	try:
		res=ia.accHitTest(x,y)
		if isinstance(res,IAccessible):
			new_ia=res
			new_child=0
		elif isinstance(res,comtypes.client.dynamic._Dispatch) or isinstance(res,comtypes.automation.IUnknown):
			new_ia=res.QueryInterface(IAccessible)
			new_child=0
		elif isinstance(res,int) and res!=child:
			new_ia=ia
			new_child=res
		else:
			return None
		return (new_ia,new_child)
	except:
		return None

def accChild(ia,child):
	try:
		res=ia.accChild(child)
		if isinstance(res,IAccessible):
			new_ia=res
			new_child=0
		elif isinstance(res,comtypes.client.dynamic._Dispatch) or isinstance(res,comtypes.automation.IUnknown):
			new_ia=res.QueryInterface(IAccessible)
			new_child=0
		elif isinstance(res,int):
			new_ia=ia
			new_child=res
		return (new_ia,new_child)
	except:
		return None

def accChildCount(ia):
	try:
		count=ia.accChildCount
	except:
		count=0
	return count

def accParent(ia,child):
	try:
		if not child:
			res=ia.accParent
			if isinstance(res,IAccessible):
				new_ia=res
				new_child=0
			elif isinstance(res,comtypes.client.dynamic._Dispatch) or isinstance(res,comtypes.automation.IUnknown):
				new_ia=res.QueryInterface(IAccessible)
				new_child=0
			else:
				raise ValueError("no IAccessible interface")
		else:
			new_ia=ia
			new_child=0
		return (new_ia,new_child)
	except:
		return None

def accNavigate(ia,child,direction):
	res=None
	try:
		res=ia.accNavigate(direction,child)
		if isinstance(res,IAccessible):
			new_ia=res
			new_child=0
		elif isinstance(res,int):
			new_ia=ia
			new_child=res
		elif isinstance(res,comtypes.client.dynamic._Dispatch) or isinstance(res,comtypes.automation.IUnknown):
			new_ia=res.QueryInterface(IAccessible)
			new_child=0
		else:
			raise RuntimeError
		return (new_ia,new_child)
	except:
		pass



def accLocation(ia,child):
	try:
		return ia.accLocation(child)
	except:
		return None

eventMap={
winUser.EVENT_SYSTEM_FOREGROUND:"foreground",
winUser.EVENT_SYSTEM_MENUSTART:"menuStart",
winUser.EVENT_SYSTEM_MENUEND:"menuEnd",
winUser.EVENT_SYSTEM_MENUPOPUPSTART:"menuStart",
winUser.EVENT_SYSTEM_MENUPOPUPEND:"menuEnd",
winUser.EVENT_SYSTEM_SCROLLINGSTART:"scrollingStart",
winUser.EVENT_SYSTEM_SWITCHSTART:"switchStart",
winUser.EVENT_SYSTEM_SWITCHEND:"switchEnd",
winUser.EVENT_OBJECT_FOCUS:"gainFocus",
winUser.EVENT_OBJECT_SHOW:"show",
winUser.EVENT_OBJECT_DESTROY:"destroy",
winUser.EVENT_OBJECT_HIDE:"hide",
winUser.EVENT_OBJECT_DESCRIPTIONCHANGE:"descriptionChange",
winUser.EVENT_OBJECT_LOCATIONCHANGE:"locationChange",
winUser.EVENT_OBJECT_NAMECHANGE:"nameChange",
winUser.EVENT_OBJECT_REORDER:"reorder",
winUser.EVENT_OBJECT_SELECTION:"selection",
winUser.EVENT_OBJECT_SELECTIONADD:"selectionAdd",
winUser.EVENT_OBJECT_SELECTIONREMOVE:"selectionRemove",
winUser.EVENT_OBJECT_SELECTIONWITHIN:"selectionWithIn",
winUser.EVENT_OBJECT_STATECHANGE:"stateChange",
winUser.EVENT_OBJECT_VALUECHANGE:"valueChange",
IA2Handler.EVENT_ACTIVE_DECENDENT_CHANGED:"gainFocus",
IA2Handler.EVENT_TEXT_CARET_MOVED:"caret",
IA2Handler.EVENT_DOCUMENT_CONTENT_CHANGED:"reorder",
}

def manageEvent(name,window,objectID,childID):
	#Ignore any events with invalid window handles
	if not winUser.isWindow(window):
		return
	desktopObject=api.getDesktopObject()
	foregroundObject=api.getForegroundObject()
	focusObject=api.getFocusObject()
	obj=None
	for testObject in [o for o in [focusObject,foregroundObject,desktopObject] if o]:
		if isinstance(testObject,NVDAObjects.IAccessible.IAccessible) and window==testObject.windowHandle and objectID==testObject.IAccessibleObjectID and childID==testObject.IAccessibleOrigChildID:
			obj=testObject
			break
	if obj is None and name not in ["hide","locationChange"]:
		obj=NVDAObjects.IAccessible.getNVDAObjectFromEvent(window,objectID,childID)
		if not obj:
			return
	if obj:
		eventHandler.manageEvent(name,obj)

def winEventCallback(handle,eventID,window,objectID,childID,threadID,timestamp):
	global lastEventParams
	try:
		#Ignore certain duplicate events
		if lastEventParams is not None and eventID==winUser.EVENT_OBJECT_FOCUS and lastEventParams==(eventID,window,objectID,childID):
			return
		lastEventParams=(eventID,window,objectID,childID)
		focusObject=api.getFocusObject()
		foregroundObject=api.getForegroundObject()
		desktopObject=api.getDesktopObject()
		navigatorObject=api.getNavigatorObject()
		mouseObject=api.getMouseObject()
		eventName=eventMap[eventID]
		#Change window objIDs to client objIDs for better reporting of objects
		if (objectID==0) and (childID==0):
			objectID=OBJID_CLIENT
		#Remove any objects that are being hidden or destroyed
		if eventName in ["hide","destroy"]:
			if isinstance(focusObject,NVDAObjects.IAccessible.IAccessible) and (window==focusObject.windowHandle) and (objectID==focusObject.IAccessibleObjectID) and (childID==focusObject.IAccessibleOrigChildID):
				#api.setFocusObject(desktopObject)
				api.setNavigatorObject(desktopObject)
				api.setMouseObject(desktopObject)
				return
			elif isinstance(foregroundObject,NVDAObjects.IAccessible.IAccessible) and (window==foregroundObject.windowHandle) and (objectID==foregroundObject.IAccessibleObjectID) and (childID==foregroundObject.IAccessibleOrigChildID):
				api.setForegroundObject(desktopObject)
				api.setMouseObject(desktopObject)
				api.setNavigatorObject(desktopObject)
				return
		#Ignore any other destroy events since the object does not exist
		if eventName=="destroy":
			return
		#Ignore events with invalid window handles
		if not window:
			window=winUser.getDesktopWindow()
		elif not winUser.isWindow(window):
			return
		windowClassName=winUser.getClassName(window)
		controlID=winUser.getControlID(window)
		#A hack to fix a bug in Notepad++ where focus is constantly given to some strange list
		if eventID==winUser.EVENT_OBJECT_FOCUS and controlID==30002 and winUser.getClassName(winUser.getAncestor(window,winUser.GA_ROOTOWNER))=="Notepad++":
			return
		if objectID==OBJID_CARET and eventName=="locationChange":
			if window==focusObject.windowHandle and isinstance(focusObject,NVDAObjects.IAccessible.IAccessible):
				eventName="caret"
				objectID=focusObject.IAccessibleObjectID
				childID=focusObject.IAccessibleChildID
			else:
				return
		#Report mouse shape changes
		if (eventID==winUser.EVENT_OBJECT_NAMECHANGE) and (objectID==OBJID_CURSOR):
			if not config.conf["mouse"]["reportMouseShapeChanges"]:
				return
			obj=NVDAObjects.IAccessible.getNVDAObjectFromEvent(winUser.getDesktopWindow(),OBJID_CURSOR,0)
			queueHandler.queueFunction(queueHandler.eventQueue,mouseHandler.updateMouseShape,obj.name)
			return
		#Process foreground events
		if eventName=="foreground":
			queueHandler.queueFunction(queueHandler.eventQueue,foreground_winEventCallback,window,objectID,childID)
			return
		#Process focus events
		elif eventName=="gainFocus":
			queueHandler.queueFunction(queueHandler.eventQueue,focus_winEventCallback,window,objectID,childID,isForegroundChange=False)
			return
		#Process IA2 active descendant events
		if eventID==IA2Handler.EVENT_ACTIVE_DECENDENT_CHANGED:
			IA2Handler.handleActiveDescendantEvent(window,objectID,childID)
			return
		#Start this event on its way through appModules, virtualBuffers and NVDAObjects
		queueHandler.queueFunction(queueHandler.eventQueue,manageEvent,eventName,window,objectID,childID)
	except:
		globalVars.log.error("winEventCallback")

def foreground_winEventCallback(window,objectID,childID):
	#Ignore any events with invalid window handles
	if not winUser.isWindow(window):
		return
	focus=api.getFocusObject()
	#Ignore foreground events for a window that is a parent of the current focus as focus ancestors would have already announced it
	if winUser.isDescendantWindow(window,focus.windowHandle):
		return
	return focus_winEventCallback(window,objectID,childID,isForegroundChange=True)

def focus_winEventCallback(window,objectID,childID,isForegroundChange=False):
	#Ignore any events with invalid window handles
	if not winUser.isWindow(window):
		return
	#Ignore focus/foreground events on the parent windows of the desktop and taskbar
	if winUser.getClassName(window) in ("Progman","Shell_TrayWnd"):
		return
	appModuleHandler.update(window)
	if JABHandler.isRunning and JABHandler.isJavaWindow(window):
		return JABHandler.event_enterJavaWindow(window)
	oldFocus=api.getFocusObject()
	if oldFocus and isinstance(oldFocus,NVDAObjects.IAccessible.IAccessible) and window==oldFocus.windowHandle and objectID==oldFocus.IAccessibleObjectID and childID==oldFocus.IAccessibleOrigChildID and winUser.getClassName(window)!="OUTEXVLB":
		return
	obj=NVDAObjects.IAccessible.getNVDAObjectFromEvent(window,objectID,childID)
	focus_manageEvent(obj,isForegroundChange)

def focus_manageEvent(obj,isForegroundChange=False,needsFocusState=True):
	if isForegroundChange:
		needsFocusState=False
	if not obj:
		return
	if obj.role==controlTypes.ROLE_UNKNOWN:
		parent=NVDAObjects.IAccessible.IAccessible._get_parent(obj)
		if parent:
			return focus_manageEvent(parent,isForegroundChange,False)
	oldFocus=api.getFocusObject()
	if obj==oldFocus:
		return
	oldAncestors=api.getFocusAncestors()
	ancestors=[]
	if needsFocusState:
		if obj.IAccessibleStates&STATE_SYSTEM_FOCUSED or obj.windowClassName.startswith("Mozilla"):
			hasFocusState=True
		else:
			hasFocusState=False
	parent=NVDAObjects.IAccessible.IAccessible._get_parent(obj)
	matchedOld=False
	oldAncestorLen=len(oldAncestors)
	while parent:
		if parent==oldFocus:
			newAncestors=list(oldAncestors)
			newAncestors.append(oldFocus)
			newAncestors.extend(ancestors)
			ancestors=newAncestors
			break
		for index in range(oldAncestorLen):
			if parent==oldAncestors[(oldAncestorLen-1)-index]:
				ancestors=oldAncestors[0:oldAncestorLen-index]+ancestors
				matchedOld=True
				break
		if matchedOld:
			break
		ancestors.insert(0,parent)
		parent=NVDAObjects.IAccessible.IAccessible._get_parent(parent)
	if needsFocusState:
		for parent in ancestors:
			if (not hasFocusState) and (parent.IAccessibleStates&STATE_SYSTEM_FOCUSED):
				hasFocusState=True
	foundGroup=False
	for index in range(len(ancestors)):
		role=ancestors[index].role
		if role==controlTypes.ROLE_WINDOW:
			continue
		if role==controlTypes.ROLE_GROUPING:
			foundGroup=True
			break
		groupObj=findGroupboxObject(ancestors[index])
		if groupObj:
			foundGroup=True
			ancestors.insert(index,groupObj)
			break
	if not foundGroup:
		groupObj=findGroupboxObject(obj)
		if groupObj:
			ancestors.append(groupObj)
	if needsFocusState:
		if not hasFocusState:
			return
	virtualBuffers.IAccessible.update(obj)
	api.setFocusObject(obj,ancestors=ancestors)
	if isForegroundChange:
		speech.cancelSpeech()
		api.setForegroundObject(obj)
	eventHandler.manageEvent("gainFocus",obj)

#Register internal object event with IAccessible
cWinEventCallback=ctypes.CFUNCTYPE(ctypes.c_voidp,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int)(winEventCallback)

def initialize():
	desktopObject=NVDAObjects.IAccessible.getNVDAObjectFromEvent(winUser.getDesktopWindow(),OBJID_CLIENT,0)
	if not isinstance(desktopObject,NVDAObjects.IAccessible.IAccessible):
		raise OSError("can not get desktop object")
	api.setDesktopObject(desktopObject)
	api.setForegroundObject(desktopObject)
	api.setFocusObject(desktopObject)
	api.setNavigatorObject(desktopObject)
	api.setMouseObject(desktopObject)
	winEventCallback(0,winUser.EVENT_SYSTEM_FOREGROUND,winUser.getForegroundWindow(),OBJID_CLIENT,0,0,0)
	focusObject=api.findObjectWithFocus()
	if isinstance(focusObject,NVDAObjects.IAccessible.IAccessible):
		winEventCallback(0,winUser.EVENT_OBJECT_FOCUS,focusObject.windowHandle,OBJID_CLIENT,0,0,0)
	for eventType in eventMap.keys():
		handle=winUser.setWinEventHook(eventType,eventType,0,cWinEventCallback,0,0,0)
		if handle:
			objectEventHandles.append(handle)
		else:
			globalVars.log.error("initialize: could not register callback for event %s (%s)"%(eventType,eventMap[eventType]))

def terminate():
	for handle in objectEventHandles:
		winUser.unhookWinEvent(handle)

def getIAccIdentityString(pacc,childID):
	p,s=pacc.QueryInterface(IAccIdentity).getIdentityString(childID)
	p=ctypes.cast(p,ctypes.POINTER(ctypes.c_char*s))
	return p.contents.raw

def findGroupboxObject(obj):
	prevWindow=winUser.getPreviousWindow(obj.windowHandle)
	while prevWindow:
		if winUser.getClassName(prevWindow)=="Button" and winUser.getWindowStyle(prevWindow)&winUser.BS_GROUPBOX:
			groupObj=NVDAObjects.IAccessible.getNVDAObjectFromEvent(prevWindow,OBJID_CLIENT,0)
			try:
				(left,top,width,height)=obj.location
				(groupLeft,groupTop,groupWidth,groupHeight)=groupObj.location
			except:
				return
			if groupObj.IAccessibleRole==ROLE_SYSTEM_GROUPING and left>=groupLeft and (left+width)<=(groupLeft+groupWidth) and top>=groupTop and (top+height)<=(groupTop+groupHeight):
				return groupObj
		prevWindow=winUser.getPreviousWindow(prevWindow)

