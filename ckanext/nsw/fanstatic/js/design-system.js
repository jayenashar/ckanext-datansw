/* PANCAKE v1.3.1 PANCAKE-JS v1.1.0 */var AU=AU||{};!function(e){function t(e,t,n){"closing"===n?e.setAttribute("aria-expanded",!1):e.setAttribute("aria-expanded",!0)}function n(e,t,n,o){if("opening"===t||"open"===t)var a=n||"au-accordion--closed",i=o||"au-accordion--open";else var a=o||"au-accordion--open",i=n||"au-accordion--closed";!function(e,t){e.classList?e.classList.remove(t):e.className=e.className.replace(new RegExp("(^|\\b)"+t.split(" ").join("|")+"(\\b|$)","gi")," ")}(e,a),function(e,t){e.classList?e.classList.add(t):e.className=e.className+" "+t}(e,i)}var o={};o.Toggle=function(o,a,i){try{window.event.cancelBubble=!0,event.stopPropagation()}catch(s){}o.length===undefined&&(o=[o]),"object"!=typeof i&&(i={});for(var l=0;l<o.length;l++){var r=o[l],c=r.getAttribute("aria-controls"),u=document.getElementById(c);if(null==u)throw new Error("AU.accordion.Toggle cannot find the target to be toggled from inside aria-controls.\nMake sure the first argument you give AU.accordion.Toggle is the DOM element (a button or a link) that has an aria-controls attribute that points to a div that you want to toggle.");u.style.display="block",function(o){e.animate.Toggle({element:u,property:"height",speed:a||250,prefunction:function(e,a){"opening"===a?(e.style.display="block","function"==typeof i.onOpen&&i.onOpen()):"function"==typeof i.onClose&&i.onClose(),t(o,0,a),n(o,a)},postfunction:function(e,t){"closed"===t?(e.style.display="",e.style.height="","function"==typeof i.afterClose&&i.afterClose()):(e.style.display="",e.style.height="","function"==typeof i.afterOpen&&i.afterOpen()),n(e,t)}})}(r)}return!1},o.Open=function(o,a){try{window.event.cancelBubble=!0,event.stopPropagation()}catch(s){}o.length===undefined&&(o=[o]);for(var i=0;i<o.length;i++){var l=o[i],r=l.getAttribute("aria-controls"),c=document.getElementById(r),u=0;u="undefined"!=typeof getComputedStyle?window.getComputedStyle(c).height:c.currentStyle.height,0===parseInt(u)&&(c.style.height="0px"),c.style.display="",n(c,"opening"),n(l,"opening"),t(l,0,"opening"),function(t,o,a){e.animate.Run({element:t,property:"height",endSize:"auto",speed:o||250,callback:function(){n(a,"opening")}})}(c,a,l)}},o.Close=function(o,a){try{window.event.cancelBubble=!0,event.stopPropagation()}catch(u){}o.length===undefined&&(o=[o]);for(var i=0;i<o.length;i++){var l=o[i],r=l.getAttribute("aria-controls"),c=document.getElementById(r);n(l,"closing"),t(l,0,"closing"),function(t,o){e.animate.Run({element:t,property:"height",endSize:0,speed:o||250,callback:function(){t.style.display="",n(t,"close")}})}(c,a)}},e.accordion=o}(AU),"undefined"!=typeof module&&(module.exports=AU);var AU=AU||{};!function(e){function t(e,t,n){if(e===t)return{stepSize:0,steps:0,intervalTime:0};var o=t-e,a=n/o,i=o<0?-1:1,l=Math.abs(o/i);return a=n/l,Math.abs(a)<1e3/60&&(a=1e3/60,i=o/(l=Math.ceil(Math.abs(n/a)))),{stepSize:i,steps:l-1,intervalTime:a}}var n={};"undefined"!=typeof module&&(n.CalculateAnimationSpecs=t),n.GetCSSPropertyBecauseIE=function(t,n){if("undefined"!=typeof getComputedStyle)return window.getComputedStyle(t)[n];var o=t.currentStyle[n];return"auto"===o&&(o=e.animate.CalculateAuto(t,n)),o},n.CalculateAuto=function(e,t){var n,o;return"height"===t?(n=e.clientHeight,e.style[t]="auto",o=e.clientHeight,e.style[t]=n+"px"):(n=e.clientWidth,e.style[t]="auto",o=e.clientWidth,e.style[t]=n+"px"),parseInt(o)},n.Stop=function(e){clearInterval(e.AUanimation)},n.Run=function(n){var o=n.element,a=n.speed||250;o.length===undefined&&(o=[o]),"function"!=typeof n.callback&&(n.callback=function(){}),o[0].AUinteration=0,o[0].AUinterations=o.length;for(var i=0;i<o.length;i++){var l=o[i];e.animate.Stop(l);var r=parseInt(e.animate.GetCSSPropertyBecauseIE(l,n.property)),c=n.endSize;"auto"===n.endSize&&(c=e.animate.CalculateAuto(l,n.property));var u=t(r,c,a),s=r;u.stepSize<0?l.AUtoggleState="closing":u.stepSize>0&&(l.AUtoggleState="opening"),function(t,a,i,l,r){t.AUanimation=setInterval(function(){if(a===r||0===l.steps){if(e.animate.Stop(t),t.style[n.property]=r+"px",t.AUtoggleState="",o[0].AUinteration++,"auto"===n.endSize&&(t.style[n.property]=""),o[0].AUinteration>=o[0].AUinterations)return n.callback()}else i+=l.stepSize,t.style[n.property]=i+"px",l.steps--},Math.abs(l.intervalTime))}(l,r,s,u,c)}},n.Toggle=function(t){var n=t.element,o=t.property||"height",a=t.speed||250,i=t.closeSize===undefined?0:t.closeSize,l=t.openSize===undefined?"auto":t.openSize;n.length===undefined&&(n=[n]),"function"!=typeof t.prefunction&&(t.prefunction=function(){}),"function"!=typeof t.postfunction&&(t.postfunction=function(){}),"function"!=typeof t.callback&&(t.callback=function(){}),n[0].AUtoggleInteration=0,n[0].AUtoggleInterations=n.length;for(var r=0;r<n.length;r++){var c=n[r];e.animate.Stop(c);var u,s="",p="",f=parseInt(e.animate.GetCSSPropertyBecauseIE(c,t.property));if(f===i||"closing"===c.AUtoggleState)u=l,s="opening",p="open";else{if(f===i&&"opening"!==c.AUtoggleState)throw new Error("AU.animate.Toggle cannot determine state of element");u=i,s="closing",p="closed"}t.prefunction(c,s),e.animate.Run({element:c,endSize:u,property:o,speed:a,callback:function(){if(n[0].AUtoggleInteration++,n[0].AUtoggleInteration===n[0].AUinterations){var e=t.callback(c,p);return t.postfunction(c,p),e}t.postfunction(c,p)}})}},e.animate=n}(AU),"undefined"!=typeof module&&(module.exports=AU),"undefined"!=typeof exports&&(Object.defineProperty(exports,"__esModule",{value:!0}),eval("exports.default = AU"));var AU=AU||{};!function(e){function t(e,t,n,o){if("opening"===t||"open"===t)var a=n||"au-main-nav__content--closed",i=o||"au-main-nav__content--open";else var a=o||"au-main-nav__content--open",i=n||"au-main-nav__content--closed";!function(e,t){e.classList?e.classList.remove(t):e.className=e.className.replace(new RegExp("(^|\\b)"+t.split(" ").join("|")+"(\\b|$)","gi")," ")}(e,a),function(e,t){e.classList?e.classList.add(t):e.className=e.className+" "+t}(e,i)}function n(e,t,n){function o(e){var t=n.apply(this,arguments);return!1===t&&(e.stopPropagation(),e.preventDefault()),t}function a(){var t=n.call(e,window.event);return!1===t&&(window.event.returnValue=!1,window.event.cancelBubble=!0),t}return e.addEventListener?(e.addEventListener(t,o,!1),{element:e,handler:o,event:t}):(e.attachEvent("on"+t,a),{element:e,handler:a,event:t})}function o(e){e.element.removeEventListener?e.element.removeEventListener(e.event,e.handler):e.element.detachEvent("on"+e.event,e.handler)}var a={},i={},l=!1;a.Toggle=function(r,c,u){if(!l){l=!0;try{window.event.cancelBubble=!0,event.stopPropagation()}catch(U){}"object"!=typeof u&&(u={});var s=r.getAttribute("aria-controls"),p=document.getElementById(s),f=p.querySelector(".au-main-nav__menu"),d=p.querySelector(".au-main-nav__overlay"),g=p.querySelector(".au-main-nav__toggle--close"),y=p.querySelector(".au-main-nav__toggle--open"),m=p.querySelector(".au-main-nav__focus-trap-top"),v=p.querySelector(".au-main-nav__focus-trap-bottom"),h=f.querySelectorAll("a, .au-main-nav__toggle"),b=-1===p.className.indexOf("au-main-nav__content--open"),A=f.offsetWidth,S=b?"opening":"";d.style.display="block",function(c,s){e.animate.Toggle({element:f,property:"left",openSize:0,closeSize:-1*A,speed:s||250,prefunction:function(){"opening"===S?(f.style.display="block",d.style.left=0,d.style.opacity=.5,"function"==typeof u.onOpen&&u.onOpen()):(d.style.opacity="0","function"==typeof u.onClose&&u.onClose())},postfunction:function(){"opening"===S?(g.focus(),m.setAttribute("tabindex",0),v.setAttribute("tabindex",0),i.focusTop=n(m,"focus",function(){h[h.length-1].focus()}),i.focusBottom=n(v,"focus",function(){h[0].focus()}),i.escKey=n(document,"keyup",function(){var e=e||window.event,t=function(e,t){return("undefined"!=typeof getComputedStyle?getComputedStyle(e,null):e.currentStyle).display}(d);27===e.keyCode&&"block"===t&&a.Toggle(r,s,u)}),"function"==typeof u.afterOpen&&u.afterOpen()):(y.focus(),m.removeAttribute("tabindex"),v.removeAttribute("tabindex"),o(i.focusTop),o(i.focusBottom),o(i.escKey),"function"==typeof u.afterClose&&u.afterClose()),t(c,S),t(document.body,S,"au-main-nav__scroll--unlocked","au-main-nav__scroll--locked"),f.style.display="",f.style.left="",d.style.display="",d.style.left="",d.style.opacity="",l=!1}})}(p,c)}},e.mainNav=a}(AU),"undefined"!=typeof module&&(module.exports=AU);var AU=AU||{};"undefined"!=typeof module&&(module.exports=AU);
