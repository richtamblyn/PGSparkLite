/*
	This file is part of iWin JS library by Ignas Poklad(ignas2526).
	iWin is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	iWin is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with iWin. If not, see <http://www.gnu.org/licenses/>.
*/
function iWindow()
{
	var self = this;
	self.win = {};
	self.dragwID = null;
	self.dragObj = -1;
	self.dragSTop = null;
	self.dragSleft = null;
	self.dragStartX = null;
	self.dragStartY = null;

	self.offsetTop = 0;
	self.offsetLeft = 0;
	self.offsetRight = 0;
	self.offsetBottom = 0;
	
	self.resizeWidth = null;
	self.resizeHeight = null;

	self.zwin = [];
	self.zindex = 99;

	self.scroll_length = 0;
	self.contentMinAutoWidth = 10;
	self.contentMinAutoHeight = 10;
	self.contentMaxAutoWidth = 810;
	self.contentMaxAutoHeight = 610;

	self.init = function(param)
	{
		self.onSetTitle = typeof param.onSetTitle != 'function' ? function(wID, obj, title) {obj.innerText = title;} : param.onSetTitle;


		var tmpDiv = document.createElement('div');
		tmpDiv.style.cssText = 'position:aboslute;top:-99px;left:-99px;width:70px;height:70px;overflow:scroll;border:0;margin:0;padding:0';
		document.body.appendChild(tmpDiv);
		self.scroll_length = tmpDiv.offsetWidth - tmpDiv.clientWidth;
		document.body.removeChild(tmpDiv);

		// Detect if passive events are present. Added with Chrome 51, prevents preventDefault() function in the events
		self.passiveEvents = false;
		try {
		  var opts = Object.defineProperty({}, 'passive', {get: function(){self.passiveEvents = true;}});
		  window.addEventListener('test', null, opts);
		} catch (e) {}
	};

	self.create = function(param, wID)
	{
		if (typeof self.win[wID] != 'undefined') return false;
		if (typeof param.type != 'string') param.type = 'window';
		if (typeof param.class == 'string') param.class = ' ' + param.class; else param.class = '';
		
		self.win[wID] = {};
		self.win[wID].type = param.type;
		self.win[wID].tabs = {};
		self.win[wID].wID = wID;
		self.win[wID].obj = document.createElement('div');
		self.win[wID].obj.className = 'winb iwin_'+ param.type + param.class;
		self.win[wID].obj.style.cssText = "display:none;top:50px;left:20px;";
		self.win[wID].obj.innerHTML =
			'<div class="winbt" style="white-space:nowrap;overflow:hidden;"> </div>'+
			'<div class="winbb" style="display:none"> </div>'+
			'<div class="winbc"> </div>'+
			'<div class="winr tl"> </div><div class="winr tt"> </div><div class="winr tr"> </div>'+
			'<div class="winr ll"> </div><div class="winr rr"> </div>'+
			'<div class="winr bl"> </div><div class="winr bb"> </div><div class="winr br"> </div>';
		//'<div style="display:none;position:absolute;width:100%;height:100%;top:0;"></div>';// for modal window lock
		document.body.appendChild(self.win[wID].obj);
		
		self.win[wID].onShow = typeof param.onShow == 'function' ? param.onShow : function(){};
		self.win[wID].onHide = typeof param.onHide == 'function' ? param.onHide : function(){};
		self.win[wID].onClose = typeof param.onClose == 'function' ? param.onClose : function(){};
		self.win[wID].onDestroy = typeof param.onDestroy == 'function' ? param.onDestroy : function(){};
		
		// Capture phase first
		self.addEvent(self.win[wID].obj, 'press', function(){self.toFront(wID);}, true);

		// Bubble phase third: move window
		self.addEvent(self.win[wID].obj.children[0], 'start', function(e) {self.resize(wID, {moveT:1, moveL:1}, e);}, false);
		
		// Top Left
		self.addEvent(self.win[wID].obj.children[3], 'start', function(e) {self.resize(wID, {moveT:1, moveB:1, invertB:1, moveL:1, moveR:1, invertR:1}, e);}, true);
		// Top Top
		self.addEvent(self.win[wID].obj.children[4], 'start', function(e) {self.resize(wID, {moveT:1, moveB:1, invertB:1}, e);}, true);
		// Top Right
		self.addEvent(self.win[wID].obj.children[5], 'start', function(e) {self.resize(wID, {moveT:1, moveB:1, invertB:1, moveR:1}, e);}, true);

		// Left left
		self.addEvent(self.win[wID].obj.children[6], 'start', function(e) {self.resize(wID, {moveL:1, moveR:1, invertR:1}, e);}, true);
		// Right Right
		self.addEvent(self.win[wID].obj.children[7], 'start', function(e) {self.resize(wID, {moveR:1}, e);}, true);

		// Bottom Left
		self.addEvent(self.win[wID].obj.children[8], 'start', function(e) {self.resize(wID, {moveB:1, moveL:1, moveR:1, invertR:1}, e);}, true);
		// Bottom Bottom
		self.addEvent(self.win[wID].obj.children[9], 'start', function(e) {self.resize(wID, {moveB:1}, e);}, true);
		// Bottom Right
		self.addEvent(self.win[wID].obj.children[10], 'start', function(e) {self.resize(wID, {moveB:1, moveR:1}, e);}, true);

		self.win[wID].contentWidth = 0;
		self.win[wID].contentHeight = 0;
		self.win[wID].contentScrollHorizontal = false;
		self.win[wID].contentScrollVertical = false;

		self.setTitle(param.title, wID);
		return true;
	};

	self.createPlane = function(param, wID)
	{
		if (typeof self.win[wID] != 'undefined') return false;
		
		self.win[wID] = {};
		self.win[wID].type = 'plane';
		self.win[wID].wID = wID;
		self.win[wID].obj = document.createElement('div');
		self.win[wID].obj.className = 'winp';
		self.win[wID].obj.style.cssText = 'display:none;position:absolute;top:0;left:0;width:100%;height:100%';

		document.body.appendChild(self.win[wID].obj);

		self.win[wID].onShow = typeof param.onShow == 'function' ? param.onShow : function(){};
		self.win[wID].onDestroy = typeof param.onDestroy == 'function' ? param.onDestroy : function(){};
		self.win[wID].onHide = typeof param.onHide == 'function' ? param.onHide : function(){};
		self.win[wID].onClose = typeof param.onClose == 'function' ? param.onClose : function(){};
		self.win[wID].onPress = typeof param.onPress == 'function' ? param.onPress : function(){};

		// Capture phase first
		self.addEvent(self.win[wID].obj, 'press', function(e){self.win[wID].onPress(wID, e);}, true);
		return true;
	};

	self.addEvent = function(object, event, callback, bubbles, passive)
	{
		passive = typeof passive == 'undefined' ? false : passive;
		
		if (self.passiveEvents) {
			var opts = {passive: passive, capture: bubbles};
		} else {
			var opts = bubbles;
		}

		switch(event) {
			// Start implies that there will be an end event. Press means either a single click or a tap event.
			case 'start': case 'press':
				object.addEventListener('touchstart', callback, opts);
				object.addEventListener('mousedown', callback, opts);
			break;
			case 'move':
				object.addEventListener('touchmove', callback, opts);
				object.addEventListener('mousemove', callback, opts);
			break;
			case 'end':
				object.addEventListener('touchend', callback, opts);
				object.addEventListener('mouseup', callback, opts);
			break;
		}
	};

	self.removeEvent = function(object, event, callback, bubbles, passive)
	{
		passive = typeof passive == 'undefined' ? false : passive;
		if (self.passiveEvents) {
			var opts = {passive: passive, capture: bubbles};
		} else {
			var opts = bubbles;
		}

		switch(event) {
			case 'start': case 'press':
				object.removeEventListener('touchstart', callback, opts);
				object.removeEventListener('mousedown', callback, opts);
			break;
			case 'move':
				object.removeEventListener('touchmove', callback, opts);
				object.removeEventListener('mousemove', callback, opts);
			break;
			case 'end':
				object.removeEventListener('touchend', callback, opts);
				object.removeEventListener('mouseup', callback, opts);
			break;
		}
	};

	self.destroy = function(wID, e)
	{
		if (typeof self.win[wID] == 'undefined') return false;
		self.win[wID].onDestroy(wID);

		var evt = e || window.event;
		
		self.zRemove(wID);
		document.body.removeChild(self.win[wID].obj);
		delete self.win[wID];
		if (evt) (evt.stopPropagation)? evt.stopPropagation(): evt.cancelBubble = true;
		return true;
	};

	self.show = function(wID)
	{
		if (self.win[wID].obj.style.display == 'block') return false;
		self.win[wID].onShow(wID);
		self.win[wID].obj.style.display = 'block';
		self.zAdd(wID);
		return true;
	};

	self.hide = function(wID)
	{
		if (self.win[wID].obj.style.display == 'none') return false;
		self.win[wID].onHide(wID);
		self.win[wID].obj.style.display = 'none';
		self.zRemove(wID);
		return true;
	};

	self.setTitle = function(title, wID)
	{
		if (typeof title == 'undefined' || !title.length) {
			self.win[wID].titlebar = false;
			self.win[wID].obj.children[0].style.display = 'none';
		} else { 
			self.win[wID].titlebar = true;
			self.win[wID].obj.children[0].style.display = 'block';
			self.onSetTitle(wID, self.win[wID].obj.children[0], title);
		}
		return true;
	};

	self.setContent = function(content, wID)
	{
		self.win[wID].obj.children[2].innerHTML = content;
		return true;
	};

	self.setContentDimensions = function(param, wID)
	{
		if (!param) param = {};
		if (typeof param.width == 'undefined') param.width = 'auto';
		if (typeof param.height == 'undefined') param.height = 'auto';

		var posTop = self.win[wID].obj.offsetTop, posLeft = self.win[wID].obj.offsetLeft;
		self.win[wID].obj.style.top = '-9999px';
		self.win[wID].obj.style.left = '-9999px';
		var isHidden = self.show(wID);

		var visibleTab = null;
		if (param.width == 'auto' || param.height == 'auto') {
			self.win[wID].obj.children[2].style.width = 'auto';
			self.win[wID].obj.children[2].style.height = 'auto';
			self.win[wID].obj.children[2].style.overflow = 'hidden'; // impartant for proper height calculations

			// Make all tabs visible before computing height
			for (var tID in self.win[wID].tabs) {
				if (self.win[wID].tabs[tID].contentObj.style.display == 'block') {
					visibleTab = tID;
				} else {
					self.win[wID].tabs[tID].contentObj.style.display = 'block';
				}
			}
		}

		var ContentRect = self.win[wID].obj.children[2].getBoundingClientRect();

		if (param.width == 'auto') {
			self.win[wID].contentWidth = ContentRect.width;
		} else {
			self.win[wID].contentWidth = parseInt(param.width, 10);
		}

		if (param.height == 'auto') {
			self.win[wID].contentHeight = ContentRect.height;
		} else {
			self.win[wID].contentHeight = parseInt(param.height, 10);
		}

		if (self.win[wID].contentWidth < self.contentMinAutoWidth) self.win[wID].contentWidth = self.contentMinAutoWidth;
		else if (self.win[wID].contentWidth > self.contentMaxAutoWidth) self.win[wID].contentWidth = self.contentMaxAutoWidth;

		self.win[wID].obj.children[2].style.width = self.win[wID].contentWidth + 'px';

		if (self.win[wID].contentHeight > self.contentMaxAutoHeight) {
			self.win[wID].contentHeight = self.contentMaxAutoHeight;
			self.win[wID].contentScroll = true;
		} else if (self.win[wID].contentHeight < self.contentMinAutoHeight) self.win[wID].contentHeight = self.contentMinAutoHeight;

		self.win[wID].obj.children[2].style.height = self.win[wID].contentHeight + 'px';

		// Set tabs back
		if (visibleTab) {
			for (var tID in self.win[wID].tabs) {
				if (tID == visibleTab) {
					self.win[wID].tabs[tID].contentObj.style.display = 'block';
				} else {
					self.win[wID].tabs[tID].contentObj.style.display = 'none';
				}
			}
		}
		
		self.setWindowOption({
			contentScrollHorizontal: self.win[wID].contentScrollHorizontal,
			contentScrollVertical: self.win[wID].contentScrollVertical
		}, wID);
		
		self.win[wID].obj.style.top = posTop + 'px';
		self.win[wID].obj.style.left = posLeft + 'px';

		if (isHidden) self.hide(wID);

		return true;
	};

	self.setContentScroll = function(scrollHorizontal, scrollVertical, wID)
	{
		self.win[wID].contentScrollHorizontal = scrollHorizontal ? true : false;
		self.win[wID].contentScrollVertical = scrollVertical ? true : false;

		if (self.win[wID].contentScrollVertical) {
			self.win[wID].obj.children[2].style.overflowY = 'scroll';
			self.win[wID].obj.children[2].style.width = (self.win[wID].contentWidth + self.scroll_length) + 'px';
		} else {
			self.win[wID].obj.children[2].style.overflowY = 'hidden';
			self.win[wID].obj.children[2].style.width = self.win[wID].contentWidth + 'px';
		}

		if (self.win[wID].contentScrollHorizontal) {
			self.win[wID].obj.children[2].style.overflowX = 'scroll';
			self.win[wID].obj.children[2].style.height = (self.win[wID].contentHeight + self.scroll_length) + 'px';
		} else {
			self.win[wID].obj.children[2].style.overflowX = 'hidden';
			self.win[wID].obj.children[2].style.height = self.win[wID].contentHeight + 'px';
		}

		return true;
	};

	self.setPosition = function(params, wID)
	{
		var offsetTop = params.confined ? self.offsetTop : 0;
		var offsetLeft = params.confined ? self.offsetLeft : 0;
		var top, left;

		if (typeof params.top != 'undefined' && typeof params.left != 'undefined') {
			top = parseInt(params.top, 10);
			if (top < offsetTop) top = offsetTop;
			
			left = parseInt(params.left, 10);
			if (left < offsetLeft) left = offsetLeft;
			
		} else {
			return false;
		}

		self.win[wID].obj.style.top = top + 'px';
		self.win[wID].obj.style.left = left + 'px';
	};


	self.showTab = function(tID, wID)
	{
		for (var _tID in self.win[wID].tabs) {
			if (tID == _tID) {
				self.win[wID].tabs[_tID].contentObj.style.display = 'block';
				self.win[wID].tabs[_tID].tabObj.classList.add('open');
			} else {
				self.win[wID].tabs[_tID].contentObj.style.display = 'none';
				self.win[wID].tabs[_tID].tabObj.classList.remove('open');
			}
		}
		return true;
	};

	self.setTabs = function(tabs, wID)
	{
		self.win[wID].tabs = {};
		var first = null;
		self.win[wID].obj.children[1].innerHTML = '';
		for (var id in tabs) {
			var contentObj = self.win[wID].obj.children[2].querySelectorAll('[data-iwin-tabid="'+id+'"]')[0];
			if (typeof(contentObj) == 'undefined') continue;
			
			var tabObj = document.createElement('div');
			tabObj.className = 'winbbt';
			(function(id, wID){tabObj.onclick = function(e){self.showTab(id, wID);};})(id, wID);
			tabObj.innerHTML = tabs[id];

			self.win[wID].tabs[id] = {text:tabs[id], tabObj:tabObj, contentObj:contentObj};
			if (first == null) {first = id;}
			
			self.win[wID].obj.children[1].appendChild(tabObj);
		}
		
		if (first != null) {
			self.win[wID].obj.children[1].style.display = 'table';
			self.showTab(first, wID);
		} else {
			self.win[wID].obj.children[1].style.display = 'none';
		}
		return true;
	};

	self.zAdd = function(wID)
	{
		// Already added
		if (self.zwin.indexOf(wID) != -1) return false;

		self.zindex++;
		self.win[wID].obj.style.zIndex = self.zindex;
		self.zwin[self.zindex] = wID;

		return true;
	};

	self.zRemove = function(wID)
	{
		var zID = self.zwin.indexOf(wID);

		// Already removed
		if (zID == -1) return false;

		for (var i = zID + 1, end = self.zindex + 1; i < end; i++) {
			var wID2 = self.zwin[i];
			self.zwin[i - 1] = wID2;
			self.win[wID2].obj.style.zIndex = i - 1;
		}

		delete self.zwin[self.zindex];
		self.zindex--;

		return true;
	};

	self.toFront = function(wID)
	{
		var zID = self.zwin.indexOf(wID);
		if (zID == -1) return false;

		if (zID != self.zindex) {
			for (var i = zID + 1, end = self.zindex + 1; i < end; i++) {
				var wID2 = self.zwin[i];
				self.zwin[i - 1] = wID2;
				self.win[wID2].obj.style.zIndex = i - 1;
			}
			self.zwin[self.zindex] = wID;
			self.win[wID].obj.style.zIndex = self.zindex;
		}

		return true;
	};

	// moveT, moveB, moveL, moveR, invertB, invertR
	//r_t, r_r, r_b, r_l, m_b, m_l
	self.resize = function(wID, params, e)
	{
		var evt = e || window.event;
		evt.preventDefault();
		
		if (self.dragObj != -1) self.MoveStop(); // there can be only one resize
		self.dragwID = wID;
		self.dragObj = self.win[wID].obj;

		if (evt.touches) {
			self.dragStartX = parseInt(evt.touches[0].clientX, 10);
			self.dragStartY = parseInt(evt.touches[0].clientY, 10);
		} else {
			self.dragStartX = evt.clientX;
			self.dragStartY = evt.clientY;
		}
		
		self.dragSTop = self.dragObj.offsetTop;
		self.dragSLeft = self.dragObj.offsetLeft;
		
		self.windowMoveT =  params.moveT ? true : false;
		self.windowMoveR =  params.moveR ? true : false;
		self.windowMoveB =  params.moveB ? true : false;
		self.windowMoveL =  params.moveL ? true : false;

		self.windowMoveInvertB =  params.invertB ? true : false;
		self.windowMoveInvertR =  params.invertR ? true : false;
		
		self.resizeWidth = self.win[wID].contentWidth + (self.win[wID].contentScrollVertical ? self.scroll_length : 0);
		self.resizeHeight = self.win[wID].contentHeight + (self.win[wID].contentScrollHorizontal ? self.scroll_length : 0);

		document.body.classList.add('nse');
		self.addEvent(document, 'move', self._windowMove, true);
		self.addEvent(document, 'end', self.MoveStop, true);
		return true;
	};

	self._windowMove = function(e)
	{
		var evt = e || window.event;
		evt.preventDefault();

		var wID = self.dragwID;

		var clientY, clientX;
		if (evt.touches) {
			clientX = parseInt(evt.touches[0].clientX, 10);
			clientY = parseInt(evt.touches[0].clientY, 10);
		} else {
			clientX = evt.clientX;
			clientY = evt.clientY;
		}
		
		if (self.windowMoveB) {
			if (self.windowMoveInvertB && (self.resizeHeight - clientY + self.dragStartY) < self.contentMinHeight) {
				clientY = -self.contentMinHeight + self.dragStartY + self.resizeHeight;
			} else if (!self.windowMoveInvertB && (self.resizeHeight + clientY - self.dragStartY) < self.contentMinHeight) {
				clientY = self.contentMinHeight + self.dragStartY - self.resizeHeight;
			}
		}

		if (self.windowMoveT && (self.dragSTop + clientY - self.dragStartY) < self.offsetTop) {
			clientY = self.offsetTop + self.dragStartY - self.dragSTop;
		}

		if (self.windowMoveR) {
			if (self.windowMoveInvertR && (self.resizeWidth - clientX + self.dragStartX) < self.contentMinWidth) {
				clientX = -self.contentMinWidth + self.dragStartX + self.resizeWidth;
			} else if (!self.windowMoveInvertR && (self.resizeWidth + clientX - self.dragStartX) < self.contentMinWidth) {
				clientX = self.contentMinWidth + self.dragStartX - self.resizeWidth;
			}
		}

		if (self.windowMoveL && (self.dragSLeft + clientX - self.dragStartX) < self.offsetLeft) {
			clientX = self.offsetLeft + self.dragStartX - self.dragSLeft;
		}

		if (self.windowMoveT) {
			var NewWindowY = self.dragSTop + clientY - self.dragStartY;

			if (NewWindowY > (window.innerHeight - 10)) NewWindowY = window.innerHeight - 10;
			self.dragObj.style.top = NewWindowY + 'px';
		}

		if (self.windowMoveB) {
			if (self.windowMoveInvertB) {
				self.win[wID].contentHeight = self.resizeHeight - clientY + self.dragStartY;
			} else {
				self.win[wID].contentHeight = self.resizeHeight + clientY - self.dragStartY;
			}
			
			self.win[wID].obj.children[2].style.height = self.win[wID].contentHeight + 'px';
		}

		if (self.windowMoveL) {
			var NewWindowX = self.dragSLeft + clientX - self.dragStartX;
			
			if (NewWindowX > (window.innerWidth - 10)) NewWindowX = window.innerWidth - 10;
			
			self.dragObj.style.left = NewWindowX + 'px';
		}

		if (self.windowMoveR) {
			if (self.windowMoveInvertR) {
				self.win[wID].contentWidth = self.resizeWidth - clientX + self.dragStartX;
			} else {
				self.win[wID].contentWidth = self.resizeWidth + clientX - self.dragStartX;
			}
			
			self.win[wID].obj.children[0].style.width = self.win[wID].contentWidth + 'px';
			self.win[wID].obj.children[2].style.width = self.win[wID].contentWidth + 'px';
		}
	};

	self.MoveStop = function(e)
	{
		var evt = e || window.event;
		evt.preventDefault();

		document.body.classList.remove('nse');
		self.removeEvent(document, 'move', self._windowMove, true);
		self.removeEvent(document, 'end', self.MoveStop, true);

		self.dragObj = -1;

		if (document.selection && document.selection.empty) {document.selection.empty();} else if (window.getSelection) {window.getSelection().removeAllRanges();}				
	};

	self.setWindowOption = function(options, wID)
	{
		if (typeof self.win[wID] == 'undefined' || typeof options != 'object') return false;

		for (var name in options) {
			var val = options[name];

			switch (name) {
				case 'contentScrollHorizontal':
					self.win[wID].contentScrollHorizontal = val ? true : false;
					if (self.win[wID].contentScrollHorizontal) {
						self.win[wID].obj.children[2].style.overflowX = 'scroll';
					} else {
						self.win[wID].obj.children[2].style.overflowX = 'hidden';
					}
					break;

				case 'contentScrollVertical':
					self.win[wID].contentcontentScrollVertical = val ? true : false;
					if (self.win[wID].contentcontentScrollVertical) {
						self.win[wID].obj.children[2].style.overflowY = 'scroll';
					} else {
						self.win[wID].obj.children[2].style.overflowY = 'hidden';
					}
					break;
			}
		}

		return true;
	};
	
	self.messageBox = function(msg, params, _wID)
	{
		// TOOD: _wID will be used in future for modal messageBox
		var wID = 'iAlert' + new Date().getTime().toString(36) + parseInt(Math.random() * 72).toString(36);
		self.create({title: params.title, onClose:self.destroy, type:'message'}, wID);
		self.setContent(msg, wID);
		self.setContentDimensions(null, wID);
		self.setPosition({top:'center', left:'center'}, wID);
		self.show(wID);
		self.toFront(wID);
		if (typeof params.timeout != 'undefined')
			setTimeout(function(e){self.destroy(wID, e);}, parseInt(params.timeout, 10));
		return wID;
	};

	self.createSelect = function(params, wID)
	{
		if (typeof wID == 'undefined') wID = 'selfSelectBox_'+ new Date().getTime().toString(36) + parseInt(Math.random() * 72).toString(36);

		if (!self.create({
			onClose: function(wID){self.hide(wID); self.hide(wID+ 'p')},
			onShow: function(wID){self.show(wID+ 'p')},
			onDestroy: function(wID){self.destroy(wID+ 'p')},
			onHide: function(wID){self.hide(wID+ 'p')},
			class: params.class,
			type: 'select'}, wID)) return false;

		self.createPlane({onPress:function(wID, e){
			var evt = e || window.event;
			self.hide(wID.slice(0,-1));
			self.hide(wID);
			evt.preventDefault();
		}}, wID + 'p');
		self.win[wID].callback = typeof params.callback == 'function' ? params.callback : function(){};
		
		if (typeof params.options != 'undefined') {
			var content = '';
			for (option in params.options) {
				content += '<div class="option option_'+ option+ '"onclick="self.onSelectOption('+ option+ ',\''+ wID+ '\')">' + params.options[option] + '</div>';
			}
			self.setContent(content, wID);
		}

		self.setWindowOption({'resizable': false}, wID);
		return wID;
	};

	self.onSelectOption = function(option, wID)
	{
		self.hide(wID); self.hide(wID+ 'p');
		self.win[wID].callback(option, wID);
	};
}
var iWin = new iWindow();
