/*!
 * alerty v0.0.1 (https://github.com/undead25/alerty#readme)
 * Copyright 2016 undead25
 * Licensed under the MIT license
 */
(function () {
  'use strict';

  // common function which is often using
  var commonUse = {
    /**
     * [Add class to element]
     *
     * @param el {Object}   -- element.
     * @param cls {String}  -- classes.
     */
    addClass: function(el, cls) {
      var elClass = el.className;
      var blank = (elClass !== '') ? ' ' : '';
      var added = elClass + blank + cls;
      el.className = added;
    },

    /**
     * [Remove class from element]
     *
     * @param el {Object}   -- element.
     * @param cls {String}  -- classes.
     */
    removeClass: function(el, cls) {
      var elClass = ' '+el.className+' ';
      elClass = elClass.replace(/(\s+)/gi, ' ');
      var removed = elClass.replace(' '+cls+' ', ' ');
      removed = removed.replace(/(^\s+)|(\s+$)/g, '');
      el.className = removed;
    },

    /**
     * [if element has some class]
     *
     * @param el {Object}   -- element.
     * @param cls {String}  -- classes.
     *
     * @return  {Boolean}   -- true or false.
     */
    hasClass: function(el, cls) {
      var elClass = el.className;
      var elClassList = elClass.split(/\s+/);
      var x = 0;
      for(x in elClassList) {
        if(elClassList[x] == cls) {
          return true;
        }
      }
      return false;
    },

    /**
     * [add event to some element, dom0, dom1, supports fuck ie]
     *
     * @param el {Object}       -- element.
     * @param type {String}     -- event type, such as 'click', 'mouseover'.
     * @param func {Function}   -- function.
     *
     */
    addEvent: function(el, type, func) {
      if(el.addEventListener) {
        el.addEventListener(type, func, false);
      } else if(el.attachEvent){ 
        el.attachEvent('on' + type, func);
      } else{ 
        el['on' + type] = func; 
      }  
    },

    /**
     * [remove event to some element, dom0, dom1, supports fuck ie]
     *
     * @param el {Object}       -- element.
     * @param type {String}     -- event type, such as 'click', 'mouseover'.
     * @param func {Function}   -- function.
     *
     */
    removeEvent: function(el, type, func) {
      if (el.removeEventListener){ 
        el.removeEventListener(type, func, false);
      } else if (el.detachEvent){
        el.detachEvent('on' + type, func);
      } else {
        delete el['on' + type];
      }
    },

    /**
     * [Remove element node]
     *
     * @param el {Object}   -- element.
     *
     */
    removeElement: function(el) {
      (el && el.parentNode) && el.parentNode.removeChild(el);
    },

    /**
     * [Set unique id]
     *
     * @param prefix {String}   -- id prefix name.
     *
     * @return  {String}
     */
    setUid: function(prefix) {
      do prefix += Math.floor(Math.random() * 1000000);
      while (document.getElementById(prefix));
      return prefix;
    }
  };

  /**
   * [Alertiy public API]
   *
   * @return {Object}
   */
  var Alerty = function() {

    // private object for Alerty object inherit
    var Dialog = {
      
      // static defaults params
      defaults: {
        okLabel: 'OK',
        cancelLabel: 'CANCEL',
        time: 2000
      },

      previousCallback: null,  // for cache previous toasts callbak, to handle if call more than 1 alerty

      // html templates
      template: '<div class="alerty-overlay" tabindex="-1"></div>'+
                '<div class="alerty">'+
                  '<div class="alerty-title"></div>'+
                  '<div class="alerty-content">'+
                    '<p class="alerty-message"></p>'+
                    '<div class="alerty-prompt">'+
                      '<input type="text" placeholder="" value="">'+
                      '<div class="input-line"></div>'+
                    '</div>'+
                  '</div>'+
                  '<div class="alerty-action">'+
                    '<a class="btn-cancel"></a>'+
                    '<a class="btn-ok"></a>'+
                  '</div>'+
                '</div>',



      /** 
       * [Build the HTML contents]
       *
       * @param type {String}           -- get the dialog type to arrange the correspondent html content.
       * @param content {String}        -- the text contents dialog to users.
       * @param opts {Object}           -- options.
       * @param onOk {Function}         -- custom callback function after click ok button.
       * @param onCancel {Function}     -- custom callback function after click cancel button.
       */
      setup: function(type, content, opts, onOk, onCancel) {
        // for if argument opts is not given.
        var detect = typeof opts === 'function';
        if (detect) {
          onCancel = onOk;
          onOk = opts;
        }

        var $oldModal = document.querySelector('.alerty');


        // if previous modal is open, remove it and immediately callback
        if ($oldModal) {
          commonUse.removeElement($oldModal);
          var _callback = this.previousCallback;
          if (_callback) _callback();
        }

        var $wrapper = document.createElement('div');
        $wrapper.innerHTML = this.template;

        // append alerty to body
        while ($wrapper.firstChild) {
          document.body.appendChild($wrapper.firstChild);
        }

        // cache alerty dom for next use
        var $modal = document.querySelector('.alerty');
        var $overlay = document.querySelector('.alerty-overlay');
        var $title = $modal.querySelector('.alerty-title');
        var $message = $modal.querySelector('.alerty-message');
        var $btnArea = $modal.querySelector('.alerty-action');
        var $btnOk = $modal.querySelector('.btn-ok');
        var $btnCancel = $modal.querySelector('.btn-cancel');
        var $prompt = $modal.querySelector('.alerty-prompt');
        var $input = $prompt.querySelector('input');

        // set uid
        $modal.id = commonUse.setUid('alerty');
        $overlay.id = 'overlay-'+$modal.id;

        // animation show alerty
        commonUse.addClass($overlay, 'active');
        commonUse.addClass($modal, 'alerty-show');
        $message.innerHTML = content;  // set msg

        if (opts && opts.time) this.defaults.time = opts.time; // handle time if set

        if (type !== 'prompt') {
          commonUse.removeElement($prompt); // other type do not need
        } else {
          $input.focus(); // auto focus input if type prompt

          if(opts && opts.inputType) $input.setAttribute('type', opts.inputType); // handle input type, such as 'password'
          if(opts && opts.inputPlaceholder) $input.setAttribute('placeholder', opts.inputPlaceholder); // handle input placeholder
          if(opts && opts.inputValue) $input.setAttribute('value', opts.inputValue); // handle input default value 
        }

        if (type === 'toasts') {
          this.previousCallback = onOk;  // cache callback

          // rearrange template
          commonUse.removeElement($title);
          commonUse.removeElement($btnArea);
          commonUse.removeElement($overlay);
          commonUse.addClass($modal, 'toasts');

          if (opts && opts.place === 'top') commonUse.addClass($modal, 'place-top'); // handle toasts top place
          if (opts && opts.bgColor) $modal.style.backgroundColor = opts.bgColor;
          if (opts && opts.fontColor) $message.style.color =opts.fontColor;

        } else {
          commonUse.addClass(document.body, 'no-scrolling'); // body no scorll
          (opts && opts.title) ? $title.innerHTML = opts.title : commonUse.removeElement($title); // handle title if set
          (opts && opts.okLabel) ? $btnOk.innerHTML = opts.okLabel : $btnOk.innerHTML = this.defaults.okLabel; // handle ok text if set
          $modal.style.marginTop =  - $modal.offsetHeight / 2 + 'px'; // set the place to center using margin-top;

          if (type === 'confirm' || type === 'prompt') {
            (opts && opts.cancelLabel) ? $btnCancel.innerHTML = opts.cancelLabel : $btnCancel.innerHTML = this.defaults.cancelLabel; // handle cancel text if set
          } else {
            commonUse.removeElement($btnCancel); // toasts and alery type do not need cancel btn
          }
        }

        this.bindEvent($modal, onOk, onCancel); // see next
      },

      /** 
       * [Bind event to dialog]
       *
       * @param $modal {Object}       -- modal node.
       * @param: onOk {Function}      -- ok callback.
       * @param: onCancel {Function}  -- cancel callback.
       */
      bindEvent: function($modal, onOk, onCancel) {
        var that = this;
        var $btnOk = $modal.querySelector('.btn-ok');
        var $btnCancel = $modal.querySelector('.btn-cancel');

        // toasts delay hide
        if (commonUse.hasClass($modal, 'toasts')) {
          setTimeout(function() {
            // if toasts has been removed
            if (document.getElementById($modal.id) === null) return;
            that.close($modal, onOk);
          }, that.defaults.time);
        }
        // click ok button
        if ($btnOk) {
          commonUse.addEvent($btnOk, 'click', function() {
            that.close($modal, onOk);
          });
        }
        // click cancel button
        if ($btnCancel) {
          commonUse.addEvent($btnCancel, 'click', function() {
            that.close($modal, onCancel);
          });
        }
      },

      /** 
       * [Close the actived modal and remove it]
       *
       * @param: $modal {Obejct}  -- modal element to remove.
       * @param: callback {Function}  -- callback function.
       */
      close: function($modal, callback) {
        var $input = $modal.querySelector('input');
        var $overlay = document.getElementById('overlay-'+$modal.id);

        // hide alerty with animation
        commonUse.removeClass($modal, 'alerty-show');
        commonUse.addClass($modal, 'alerty-hide');

        // remove alerty and other added elements
        setTimeout(function(){
          $overlay && commonUse.removeClass($overlay, 'active'), commonUse.removeClass(document.body, 'no-scrolling');
          
          commonUse.removeElement($modal);
          commonUse.removeElement($overlay);
          if (callback) {
            setTimeout(function(){
              !$input ? callback() : callback($input.value);  // handle prompt type, callback the input value
            }, 100);
          }
        },100);
      }
    };

    return {
      // return alerty.toasts();
      toasts: function(content, opts, callback) {
        Dialog.setup('toasts', content, opts, callback);
      },

      // return alerty.alert();
      alert: function(content, opts, onOk) {
        Dialog.setup('alert', content, opts, onOk);
      },

      // return alerty.confirm();
      confirm: function(content, opts, onOk, onCancel) {
        Dialog.setup('confirm', content, opts, onOk, onCancel);
      },

      // return alerty.prompt();
      prompt: function(content, opts, onOk, oncancel) {
        Dialog.setup('prompt', content, opts, onOk, oncancel);
      }
    };
  };



  // NPM, AMD, and wndow support
  if ('undefined' !== typeof module && !! module && !! module.exports) {
    module.exports = function() {
      return new Alerty();
    };
    var obj = new Alerty();
    for (var key in obj) {
      module.exports[key] = obj[key];
    }
  } else if (typeof define === 'function' && define.amd) {
    define(function() {
      return new Alerty();
    });
  } else {
    window.alerty = new Alerty();
  }
}());