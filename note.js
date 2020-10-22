  function getTextChildByOffset(parent, offset) {
          const nodeStack = [parent];
          let curNode = null;
          let curOffset = 0;
          let startOffset = 0;
          while (curNode = nodeStack.pop()) {
              const children = curNode.childNodes;
              for (let i = children.length - 1; i >= 0; i--) {
                  nodeStack.push(children[i]);
              }
              if (curNode.nodeType === 3) {
                  startOffset = offset - curOffset;
                  curOffset += curNode.textContent.length;
                  //我怎么觉得这返回的是前一个node?offset要不要+1?
                  if (curOffset >= offset+1) {
                      break;
                  }
              }
          }
          if (!curNode) {
              curNode = parent;
          }
          return {node: curNode, offset: startOffset};
      };
  var load_mask = function (id,type,nodes,offset_start,offset_end) {
           const len=nodes.length;
           for (let index=0;index<len;index++){
              const node=nodes[index];
              const parent = document.getElementsByTagName(node.tagName)[node.index];
              //获取到node,offset先不考虑
              const find_node  =getTextChildByOffset(parent,node.offset);
              var textNode=find_node.node;
              if(index==0){
                   textNode.splitText(offset_start);
                   textNode=textNode.nextSibling;
                   if(len==1){
                       textNode.splitText(offset_end-offset_start);
                   }
              }else if(index==len-1){
                   textNode.splitText(offset_end);
              }
              const wrap = document.createElement('high_light-span');
              if(type==1){
              wrap.setAttribute('class', 'high_light');
              }else{
              wrap.setAttribute('class', 'high_red_light');
              }
              //不能使用id，因为会造成id重复
              wrap.setAttribute("mask_id",id);
              wrap.appendChild(textNode.cloneNode(false));
              const parentNode=textNode.parentNode;
              parentNode.replaceChild(wrap,textNode);
           }
      };
function getTextPreOffset(parentNode, textNode) {
    const nodeStack = [parentNode];
    let curNode = null;
    let offset = 0;
    while (curNode = nodeStack.pop()) {
        const children = curNode.childNodes;
        for (let i = children.length - 1; i >= 0; i--) {
            nodeStack.push(children[i]);
        }

        if (curNode.nodeType === 3 && curNode !== textNode) {
            offset = offset+curNode.textContent.length;
        }
        else if (curNode.nodeType === 3) {
            break;
        }
    }
    return offset;
};

function serialize(textNode,root=document){
    const parentNode = textNode.parentNode;
    let offset=getTextPreOffset(parentNode,textNode);
    const tagName = parentNode.tagName;
    const list = root.getElementsByTagName(tagName);
    let pass_num=0;
    for (let index = 0; index < list.length; index++) {
        if (parentNode === list[index]) {
             const tmp=index-pass_num;
             return {tagName, index:tmp, offset};
        }
    }
    return {tagName, index: -1, offset};
};
function getSelectionNodes() {
    var sel = window.getSelection();
    const nodes = [];
    if (sel.rangeCount) {
        var range =sel.getRangeAt(0);
        const start = {
            node: range.startContainer,
            offset: range.startOffset
        };
        const end = {
            node: range.endContainer,
            offset: range.endOffset
        };

        let withinSelectedRange = false;
        var parent=document.body;
        const stack = [];
        stack.push(parent);
        while(stack.length){
            const item = stack.pop();
            const len = item.childNodes.length;
            if(item.nodeType&&item.nodeType==3){
                    let str = item.textContent.trim();
                    if (str.length >0) {
                        if(start.node==item){
                            withinSelectedRange=true;
                            nodes.push(item);
                            if(start.node==end.node){
                                break;
                            }
                        }else if(end.node==item){
                            withinSelectedRange=false;
                            nodes.push(item);
                            break;
                        }else if(withinSelectedRange){
                            nodes.push(item);
                        }

                    }
                }
            for(let i = len - 1; i >= 0; i--){
                stack.push(item.childNodes[i])
            }
        }
    }
    return nodes;
};
function renderSelectionNodes(id,type) {
    const nodes=getSelectionNodes();

    const range =window.getSelection().getRangeAt(0);
    const start = {
        node: range.startContainer,
        offset: range.startOffset
    };
    const end = {
        node: range.endContainer,
        offset: range.endOffset
    };
    serializeNodes=[];
    var text="";
    nodes.forEach(node => {
        serializeNodes.push(serialize(node));
        if(start.node==node){
            node.splitText(start.offset);
            node=node.nextSibling;
            if(start.node==end.node){
                node.splitText(end.offset-start.offset);

            }
        }else if(end.node==node){
              node.splitText(end.offset);
        }

        text=text+node.textContent;
        const wrap = document.createElement('high_light-span');
        if(type==2){
        wrap.setAttribute('class', 'high_red_light');
        }else{
        wrap.setAttribute('class', 'high_light');
        }
        wrap.setAttribute("mask_id",id);
        wrap.appendChild(node.cloneNode(false));
        const parentNode=node.parentNode;
        parentNode.replaceChild(wrap,node);
        });
        const top=parseInt(document.body.scrollTop+document.documentElement.scrollTop);
        const offset_start=start.offset;
        const offset_end=end.offset;
        return {id,text,serializeNodes,offset_start,offset_end,top,type};
    };
var delete_mask=function(id){
          var span_cls="high_light-span[mask_id='"+id+"']";
          Array.prototype.forEach.call(document.querySelectorAll(span_cls), (el) => {
              let elParentNode = el.parentNode
              if(elParentNode !== document.body) {
                  while (el.firstChild){
                    elParentNode.insertBefore(el.firstChild, el)
                  }
                  elParentNode.removeChild(el)
              }
        });
    };
var scroll = function (dHeight) {
              window.scrollTo(0, dHeight)
        };
var getSelectionText = function(){
        var selection= window.getSelection();
        return  selection.toString();
    };
function loadCssCode(code){
        var style = document.createElement('style');
        style.type = 'text/css';
        style.rel = 'stylesheet';
        //for Chrome Firefox Opera Safari
        style.appendChild(document.createTextNode(code));
        //for IE
        //style.styleSheet.cssText = code;
        var head = document.getElementsByTagName('head')[0];
        head.appendChild(style);
    };
function loadJS(url,callback){
        var script = document.createElement('script'),
        fn = callback || function(){};
        script.type = 'text/javascript';
        script.onload = function(){
            fn();
        };
        script.src = url;
        document.body.appendChild(script);
    };
function SetOpacity(ev, v){
        ev.filters ? ev.style.filter = 'alpha(opacity=' + v + ')' : ev.style.opacity = v / 100;
    };
function fadeIn(elem, speed, opacity){
        speed = speed || 20;
        opacity = opacity || 100;
        elem.style.display = 'block';
        SetOpacity(elem, 0);
        var val = 0;
        (function(){
            SetOpacity(elem, val);
            val += 5;
            if (val <= opacity) {
                setTimeout(arguments.callee, speed)
            }
        })();
    };
function fadeOut(elem, speed, opacity){
            speed = speed || 20;
            opacity = opacity || 0;
            var val = 100;
            (function(){
                SetOpacity(elem, val);
                val -= 5;
                if (val >= opacity) {
                    setTimeout(arguments.callee, speed);
                }else if (val < 0) {
                    elem.style.display = 'none';
                }
            })();
        };
var _move = false; var _x, _y;
var dom_tip;
document.addEventListener('mousemove',function(e){
	if(_move){
	 dom_tip.style.left= e.clientX-5+"px";
	}});
function createDiv(sectionId){
        const div = document.createElement('div');
         div.addEventListener('mousedown',function(e){
            _move = true;
			 dom_tip=div;
         });
	    div.addEventListener('mouseup',function(e){
            _move = false;
         });
        div.addEventListener('mouseover',function(e){
            var span_cls="high_light-span[mask_id='"+sectionId+"']";
            el=document.querySelector(span_cls);
            el.classList.add("high_red_light");
         });
       div.addEventListener('mouseout',function(e){
            var span_cls="high_light-span[mask_id='"+sectionId+"']";
            el=document.querySelector(span_cls);
            el.classList.remove("high_red_light");
         });
        div.setAttribute('id',sectionId+"_tip");
        div.setAttribute('class', 'bubble_tooltip_common');
        const triRight = document.createElement('label');
        triRight.setAttribute('class', 'triRight');
        const triRightInner = document.createElement('label');
        triRightInner.setAttribute('class', 'triRightInner');
        const span = document.createElement('div');
//        span.setAttribute('id', 'bubble_tooltip_content');
        const close_elm = document.createElement('p');
        close_elm.innerHTML='<span style="float: right;" id="newsUrl">[×]</span><span style="display: block;clear: both"></span>';
//        close_elm.addEventListener('click',function(e){
//              var obj = document.getElementById(sectionId+"_tip");
//                fadeOut(obj,5,0);
//
//         });
        div.appendChild(close_elm);
        div.appendChild(triRight);
        div.appendChild(triRightInner);
        div.appendChild(span);
        var o = document.body;
        o.appendChild(div);
        return div
    };
function getClientHeight()
{
  var clientHeight=0;
  if(document.body.clientHeight&&document.documentElement.clientHeight){
   clientHeight = (document.body.clientHeight<document.documentElement.clientHeight)?document.body.clientHeight:document.documentElement.clientHeight;
  }
  else {
    clientHeight = (document.body.clientHeight>document.documentElement.clientHeight)?document.body.clientHeight:document.documentElement.clientHeight;
  }
  return clientHeight;
};
function toggleMask(sectionId){
            var span_cls="high_light-span[mask_id='"+sectionId+"']";
            el=document.querySelector(span_cls);
            el.classList.toggle("high_red_light");
            rect=el.getBoundingClientRect();
            dom_height=getClientHeight()
            if(rect.top>dom_height){
                 scroll(el.offsetTop-300);
            }
            //el.offsetTop + 'px';
};
function showToolTip(data){
            sectionId=data["sectionId"];
            notes=data["notes"];
            obj=createDiv(sectionId);
            obj2=obj.children[3];
            while (obj2.hasChildNodes()) {
                obj2.removeChild(obj2.lastChild);
            }
            for(var i = 0; i < notes.length; i++) {
                const div = document.createElement('div');
                div.innerHTML=notes[i];
                obj2.appendChild(div);
            }
            if(notes.length==0){
                obj2.innerHTML="无标注";
            }
            var span_cls="high_light-span[mask_id='"+sectionId+"']";
            el=document.querySelector(span_cls);
            toRight=document.body.firstElementChild.clientWidth-el.offsetWidth-el.offsetLeft;
            toLeft=el.offsetLeft;
            if(toLeft>toRight){
                obj.style.right = '5px';
            }else{
                obj.style.left = '5px';
            }
            obj.style.top = el.offsetTop + 'px';
            fadeIn(obj,5,100);
        };

    new QWebChannel(qt.webChannelTransport,
        function(channel) {
            window.Bridge = channel.objects.Bridge;
        }
    );
    function addImageEvent(){
       images=document.getElementsByTagName('img');
        for(var i = 0; i < images.length; i++) {
            images[i].onclick = function(e) {
                var targ = e.target;
                Bridge.callFromJs('img',targ.src);
            }
        };
    };
    function addTipEvent(){
        var spans = Array.from(document.getElementsByClassName('high_light'));
        for(var i = 0; i < spans.length; i++) {
              spans[i].onclick = function(e) {
              let data=new Array()
              data.push(e.clientX)
              data.push(e.clientY)
              data.push(this.getAttribute("mask_id"))
              Bridge.callFromJs('tip',data.join('|'));
            };
        };
    };
    addImageEvent();

