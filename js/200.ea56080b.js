"use strict";(self["webpackChunkweekly_report"]=self["webpackChunkweekly_report"]||[]).push([[200],{200:function(e,t,a){a.r(t),a.d(t,{default:function(){return ie}});var l=a(689),r=a(4348),o=a(1126),i=a(6211),c=a(9244),s=a(3725),n=a(7123),d=a(6547),u=a(6048),m=a(4581),p=a(5296),h=a(2067),g=a(4994);const x=(0,g.jB)({color:String,cycle:Boolean,delimiterIcon:{type:m.TX,default:"$delimiter"},height:{type:[Number,String],default:500},hideDelimiters:Boolean,hideDelimiterBackground:Boolean,interval:{type:[Number,String],default:6e3,validator:e=>Number(e)>0},progress:[Boolean,String],verticalDelimiters:[Boolean,String],...(0,u.ZJ)({continuous:!0,mandatory:"force",showArrows:!0})},"VCarousel"),f=(0,g.RW)()({name:"VCarousel",props:x(),emits:{"update:modelValue":e=>!0},setup(e,t){let{slots:a}=t;const r=(0,h.q)(e,"modelValue"),{t:o}=(0,p.Ym)(),i=(0,l.ref)();let s=-1;function m(){e.cycle&&i.value&&(s=window.setTimeout(i.value.group.next,+e.interval>0?+e.interval:6e3))}function x(){window.clearTimeout(s),window.requestAnimationFrame(m)}return(0,l.watch)(r,x),(0,l.watch)((()=>e.interval),x),(0,l.watch)((()=>e.cycle),(e=>{e?x():window.clearTimeout(s)})),(0,l.onMounted)(m),(0,g.Ci)((()=>{const t=u.r3.filterProps(e);return(0,l.createVNode)(u.r3,(0,l.mergeProps)({ref:i},t,{modelValue:r.value,"onUpdate:modelValue":e=>r.value=e,class:["v-carousel",{"v-carousel--hide-delimiter-background":e.hideDelimiterBackground,"v-carousel--vertical-delimiters":e.verticalDelimiters},e.class],style:[{height:(0,g.Dg)(e.height)},e.style]}),{default:a.default,additional:t=>{let{group:i}=t;return(0,l.createVNode)(l.Fragment,null,[!e.hideDelimiters&&(0,l.createVNode)("div",{class:"v-carousel__controls",style:{left:"left"===e.verticalDelimiters&&e.verticalDelimiters?0:"auto",right:"right"===e.verticalDelimiters?0:"auto"}},[i.items.value.length>0&&(0,l.createVNode)(n.K,{defaults:{VBtn:{color:e.color,icon:e.delimiterIcon,size:"x-small",variant:"text"}},scoped:!0},{default:()=>[i.items.value.map(((e,t)=>{const r={id:`carousel-item-${e.id}`,"aria-label":o("$vuetify.carousel.ariaLabel.delimiter",t+1,i.items.value.length),class:["v-carousel__controls__item",i.isSelected(e.id)&&"v-btn--active"],onClick:()=>i.select(e.id,!0)};return a.item?a.item({props:r,item:e}):(0,l.createVNode)(c.D,(0,l.mergeProps)(e,r),null)}))]})]),e.progress&&(0,l.createVNode)(d.Z,{class:"v-carousel__progress",color:"string"===typeof e.progress?e.progress:void 0,modelValue:(i.getItemIndex(r.value)+1)/i.items.value.length*100},null)])},prev:a.prev,next:a.next})})),{}}});var V=a(5126),N=a(1781);const v=(0,g.jB)({...(0,V.Y)(),...(0,N.w)()},"VCarouselItem"),w=(0,g.RW)()({name:"VCarouselItem",inheritAttrs:!1,props:v(),setup(e,t){let{slots:a,attrs:r}=t;(0,g.Ci)((()=>{const t=V.y.filterProps(e),o=N.m.filterProps(e);return(0,l.createVNode)(N.m,(0,l.mergeProps)({class:["v-carousel-item",e.class]},o),{default:()=>[(0,l.createVNode)(V.y,(0,l.mergeProps)(r,t),a)]})}))}});var y=a(9923),C=a(2886),b=a(9262),k=a(7018),_=a(6984),B=a(5399),E=a(3240),S=a(4663),D=a(7664),I=a(1743);const T=(0,g.jB)({app:Boolean,color:String,height:{type:[Number,String],default:"auto"},...(0,y.r)(),...(0,b.u)(),...(0,k.s)(),...(0,_.CK)(),...(0,E.S)(),...(0,S.X)({tag:"footer"}),...(0,D.yx)()},"VFooter"),P=(0,g.RW)()({name:"VFooter",props:T(),setup(e,t){let{slots:a}=t;const r=(0,l.ref)(),{themeClasses:o}=(0,D.NX)(e),{backgroundColorClasses:i,backgroundColorStyles:c}=(0,C.z6)((0,l.toRef)(e,"color")),{borderClasses:s}=(0,y.M)(e),{elevationClasses:n}=(0,k.j)(e),{roundedClasses:d}=(0,E.v)(e),u=(0,l.shallowRef)(32),{resizeRef:m}=(0,B.w)((e=>{e.length&&(u.value=e[0].target.clientHeight)})),p=(0,l.computed)((()=>"auto"===e.height?u.value:parseInt(e.height,10)));return(0,I.Y)((()=>e.app),(()=>{const t=(0,_.hc)({id:e.name,order:(0,l.computed)((()=>parseInt(e.order,10))),position:(0,l.computed)((()=>"bottom")),layoutSize:p,elementSize:(0,l.computed)((()=>"auto"===e.height?void 0:p.value)),active:(0,l.computed)((()=>e.app)),absolute:(0,l.toRef)(e,"absolute")});(0,l.watchEffect)((()=>{r.value=t.layoutItemStyles.value}))})),(0,g.Ci)((()=>(0,l.createVNode)(e.tag,{ref:m,class:["v-footer",o.value,i.value,s.value,n.value,d.value,e.class],style:[c.value,e.app?r.value:{height:(0,g.Dg)(e.height)},e.style]},a))),{}}});var z=a(9494),L=a(8703),F=a(1689),R=a(9663),Z=a(7424);const j={class:"about-page"},A={class:"mt-6"},X={class:"d-flex align-center mb-4"},J={class:"text-h6 font-weight-bold"},M={class:"text-body-1"},W={class:"feature-icon mb-6"},$={class:"text-h6 font-weight-bold mb-4"},q={class:"text-body-1"},O={class:"text-center",style:{width:"100%"}},Q={class:"text-h5 font-weight-bold mb-2"},U={class:"text-body-1"},Y={class:"text-h5 font-weight-bold mb-4"},K={class:"text-h4 font-weight-bold primary--text mb-4"},H={key:0,class:"text-body-1"},G={key:1,class:"text-body-2 mt-1"},ee={class:"d-flex justify-center"},te={class:"mt-6"},ae={class:"mb-4"};var le={__name:"About",setup(e){const t=[{title:"メンバーの状況が見えない",description:"週報を受け取っても、本当の課題が把握できない",icon:"mdi-eye-off"},{title:"報告が形骸化している",description:"形式的な報告で終わり、成長機会を逃している",icon:"mdi-format-list-checks"},{title:"フィードバックが難しい",description:"適切なアドバイスやサポートのタイミングを逃してしまう",icon:"mdi-message-alert"}],n=[{title:"シンプルな入力で自己評価を可視化",description:"ストレス度、タスク難易度、タスク達成度を可視化し、メンバーの状況を素早く把握できます。",icon:"mdi-chart-line"},{title:"一元管理と共有機能",description:"週次報告とフィードバックを一元管理。Webリンクでの共有も可能です。",icon:"mdi-share-variant"},{title:"AIアドバイザーによる成長支援",description:"週次報告の内容を分析し、メンバーの成長をサポートする具体的なアドバイスを提供します。",icon:"mdi-robot"}],d=o.vw.map((e=>({name:e.name,price:"free"===e.planId?"無料":`${e.price.toLocaleString()}円`,priceUnit:"free"!==e.planId,features:e.features,priceDescription:e.priceDescription}))),u=[{text:"利用規約",url:i.x0},{text:"プライバシーポリシー",url:i.wu},{text:"特定商取引法に基づく表記",url:i.Rt}],m=[{image:a(913),title:"ダッシュボード",description:"チームの状況を一目で把握できるダッシュボード画面"},{image:a(9370),title:"組織メンバーの週次報告",description:"シンプルで使いやすい週次報告入力フォーム"},{image:a(702),title:"AIアドバイザー機能",description:"週次報告の内容を分析し、複数の視点から具体的なアドバイスを提供"},{image:a(7343),title:"組織情報管理",description:"メンバーと組織の情報をシンプルに管理"},{image:a(1118),title:"週次報告設定",description:"組織に合わせた週次報告の設定が可能"},{image:a(8300),title:"週次報告レビュー",description:"メンバーの週次報告を効率的にレビュー"}],p=e=>new Promise(((t,a)=>{const l=new Image;l.onload=()=>t(l),l.onerror=a,l.src=e})),h=async()=>{try{await Promise.all(m.map((e=>p(e.image))))}catch(e){}};return(0,l.onMounted)((()=>{h()})),(e,a)=>{const o=(0,l.resolveComponent)("router-link");return(0,l.openBlock)(),(0,l.createElementBlock)("div",j,[(0,l.createVNode)(z.IZ,{class:"pa-0",fluid:""},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(z.IZ,{class:"hero-section text-center py-13"},{default:(0,l.withCtx)((()=>[a[4]||(a[4]=(0,l.createElementVNode)("p",{class:"text-h4 text-sm-h5 font-weight-bold text-indigo-darken-2 slide-up-delay hero-text"},[(0,l.createTextVNode)(" ストレスフリーな管理で"),(0,l.createElementVNode)("br"),(0,l.createTextVNode)("組織の成果をサポートする週次報告システム"),(0,l.createElementVNode)("br"),(0,l.createElementVNode)("span",{class:"logo-font text-h2 my-5"},"fluxweek")],-1)),(0,l.createVNode)(F.y,{src:r,class:"mx-auto my-4 hero-image"}),(0,l.createVNode)(c.D,{color:"primary",size:"x-large",to:"/signup",class:"px-8 elevation-4",rounded:"pill"},{default:(0,l.withCtx)((()=>[a[1]||(a[1]=(0,l.createTextVNode)(" 無料で始める ")),(0,l.createVNode)(L.wP,{end:""},{default:(0,l.withCtx)((()=>a[0]||(a[0]=[(0,l.createTextVNode)("mdi-arrow-right")]))),_:1})])),_:1}),(0,l.createElementVNode)("div",A,[a[3]||(a[3]=(0,l.createTextVNode)(" アカウントをお持ちの方はこちらから ")),(0,l.createVNode)(o,{to:"/signin"},{default:(0,l.withCtx)((()=>a[2]||(a[2]=[(0,l.createTextVNode)("サインイン")]))),_:1})])])),_:1}),(0,l.createVNode)(z.IZ,{class:"py-16"},{default:(0,l.withCtx)((()=>[a[5]||(a[5]=(0,l.createElementVNode)("h2",{class:"text-h4 text-sm-h5 font-weight-bold text-center mb-16 gradient-text"},"こんな課題はありませんか？",-1)),(0,l.createVNode)(z.Li,null,{default:(0,l.withCtx)((()=>[((0,l.openBlock)(),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(t,((e,t)=>(0,l.createVNode)(z.B6,{key:t,cols:"12",md:"4"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(s.Jn,{elevation:"4",height:"100%",rounded:"lg",hover:"",class:"problem-card"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(s.OQ,{class:"pa-8"},{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("div",X,[(0,l.createVNode)(L.wP,{size:"32",color:"primary",class:"mr-4"},{default:(0,l.withCtx)((()=>[(0,l.createTextVNode)((0,l.toDisplayString)(e.icon),1)])),_:2},1024),(0,l.createElementVNode)("h3",J,(0,l.toDisplayString)(e.title),1)]),(0,l.createElementVNode)("p",M,(0,l.toDisplayString)(e.description),1)])),_:2},1024)])),_:2},1024)])),_:2},1024))),64))])),_:1})])),_:1}),(0,l.createVNode)(z.IZ,{class:"py-16"},{default:(0,l.withCtx)((()=>[a[6]||(a[6]=(0,l.createElementVNode)("h2",{class:"text-h4 text-sm-h5 font-weight-bold text-center mb-16 gradient-text"},"システムの特徴",-1)),(0,l.createVNode)(z.Li,null,{default:(0,l.withCtx)((()=>[((0,l.openBlock)(),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(n,((e,t)=>(0,l.createVNode)(z.B6,{key:t,cols:"12",md:"4"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(s.Jn,{elevation:"2",height:"100%",rounded:"lg",hover:"",class:"feature-card"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(s.OQ,{class:"pa-8"},{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("div",W,[(0,l.createVNode)(L.wP,{size:"36",color:"primary"},{default:(0,l.withCtx)((()=>[(0,l.createTextVNode)((0,l.toDisplayString)(e.icon),1)])),_:2},1024)]),(0,l.createElementVNode)("h3",$,(0,l.toDisplayString)(e.title),1),(0,l.createElementVNode)("p",q,(0,l.toDisplayString)(e.description),1)])),_:2},1024)])),_:2},1024)])),_:2},1024))),64))])),_:1})])),_:1}),(0,l.createVNode)(z.IZ,{class:"py-16"},{default:(0,l.withCtx)((()=>[a[7]||(a[7]=(0,l.createElementVNode)("h2",{class:"text-h4 text-sm-h5 font-weight-bold text-center mb-16 gradient-text"},"主な機能と画面",-1)),(0,l.createVNode)(f,{cycle:"",progress:"primary","show-arrows":"hover",height:"840",class:"elevation-4 rounded-lg"},{default:(0,l.withCtx)((()=>[((0,l.openBlock)(),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(m,((e,t)=>(0,l.createVNode)(w,{key:t},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(Z.i,{class:"d-flex align-center justify-center pb-8",height:"100%"},{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("div",O,[(0,l.createVNode)(F.y,{src:e.image,alt:e.title,class:"mx-auto mb-4","max-height":"680",contain:""},null,8,["src","alt"]),(0,l.createElementVNode)("h3",Q,(0,l.toDisplayString)(e.title),1),(0,l.createElementVNode)("p",U,(0,l.toDisplayString)(e.description),1)])])),_:2},1024)])),_:2},1024))),64))])),_:1})])),_:1}),(0,l.createVNode)(z.IZ,{class:"py-16"},{default:(0,l.withCtx)((()=>[a[10]||(a[10]=(0,l.createElementVNode)("h2",{class:"text-h4 text-sm-h5 font-weight-bold text-center mb-16 gradient-text"},"料金プラン",-1)),(0,l.createVNode)(z.Li,null,{default:(0,l.withCtx)((()=>[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)((0,l.unref)(d),(e=>((0,l.openBlock)(),(0,l.createBlock)(z.B6,{key:e.name,cols:"12",md:"4"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(s.Jn,{elevation:"2",height:"100%",rounded:"lg",class:"price-card"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(s.OQ,{class:"pa-6 text-center"},{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("h3",Y,(0,l.toDisplayString)(e.name),1),(0,l.createElementVNode)("div",K,[(0,l.createTextVNode)((0,l.toDisplayString)(e.price)+" ",1),e.priceUnit?((0,l.openBlock)(),(0,l.createElementBlock)("span",H,"/月")):(0,l.createCommentVNode)("",!0),e.priceDescription?((0,l.openBlock)(),(0,l.createElementBlock)("p",G,[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(e.priceDescription,((e,t)=>((0,l.openBlock)(),(0,l.createElementBlock)("span",{key:t},[(0,l.createTextVNode)((0,l.toDisplayString)(e),1),a[8]||(a[8]=(0,l.createElementVNode)("br",null,null,-1))])))),128))])):(0,l.createCommentVNode)("",!0)]),(0,l.createElementVNode)("div",ee,[(0,l.createVNode)(R.x8,{density:"compact",class:"features-list text-left"},{default:(0,l.withCtx)((()=>[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(e.features,((e,t)=>((0,l.openBlock)(),(0,l.createBlock)(R.gc,{key:t},{prepend:(0,l.withCtx)((()=>[(0,l.createVNode)(L.wP,{color:"primary"},{default:(0,l.withCtx)((()=>a[9]||(a[9]=[(0,l.createTextVNode)(" mdi-check-circle ")]))),_:1})])),default:(0,l.withCtx)((()=>[(0,l.createTextVNode)(" "+(0,l.toDisplayString)(e),1)])),_:2},1024)))),128))])),_:2},1024)])])),_:2},1024)])),_:2},1024)])),_:2},1024)))),128))])),_:1})])),_:1}),(0,l.createVNode)(Z.i,{color:"menu",class:"py-10 mt-16"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(z.IZ,{class:"text-center"},{default:(0,l.withCtx)((()=>[a[15]||(a[15]=(0,l.createElementVNode)("h2",{class:"text-h5 font-weight-bold text-white mb-4"}," メンバーの成長をサポートする新しい週次報告を始めましょう ",-1)),a[16]||(a[16]=(0,l.createElementVNode)("p",{class:"text-h6 font-weight-regular text-white mb-8"}," フリープランで fluxweek の価値を体験してください ",-1)),(0,l.createVNode)(c.D,{color:"primary",size:"x-large",to:"/signup",class:"px-8 elevation-4",rounded:"pill"},{default:(0,l.withCtx)((()=>[a[12]||(a[12]=(0,l.createTextVNode)(" 無料で始める ")),(0,l.createVNode)(L.wP,{end:""},{default:(0,l.withCtx)((()=>a[11]||(a[11]=[(0,l.createTextVNode)("mdi-arrow-right")]))),_:1})])),_:1}),(0,l.createElementVNode)("div",te,[a[14]||(a[14]=(0,l.createTextVNode)(" アカウントをお持ちの方はこちらから ")),(0,l.createVNode)(o,{to:"/signin",class:"text-white"},{default:(0,l.withCtx)((()=>a[13]||(a[13]=[(0,l.createTextVNode)("サインイン")]))),_:1})])])),_:1})])),_:1}),(0,l.createVNode)(P,{color:"grey-darken-3",class:"py-8"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(z.IZ,{class:"text-center"},{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("div",ae,[((0,l.openBlock)(),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(u,(e=>(0,l.createVNode)(c.D,{key:e.url,href:e.url,variant:"text",class:"text-white mx-2"},{default:(0,l.withCtx)((()=>[(0,l.createTextVNode)((0,l.toDisplayString)(e.text),1)])),_:2},1032,["href"]))),64))]),a[17]||(a[17]=(0,l.createElementVNode)("p",{class:"text-white text-body-2"},"© 2024 fluxweek All rights reserved.",-1))])),_:1})])),_:1})])),_:1})])}}},re=a(6262);const oe=(0,re.A)(le,[["__scopeId","data-v-562d380a"]]);var ie=oe},913:function(e,t,a){e.exports=a.p+"img/a1_dashborad.ffd66585.png"},7343:function(e,t,a){e.exports=a.p+"img/a2_organization.0ce07c03.png"},1118:function(e,t,a){e.exports=a.p+"img/a3_request.9d3b90c3.png"},8300:function(e,t,a){e.exports=a.p+"img/a4_review.8c575156.png"},9370:function(e,t,a){e.exports=a.p+"img/b1_report.33f96d3f.png"},702:function(e,t,a){e.exports=a.p+"img/b2_advice.aa6a382f.png"},7424:function(e,t,a){a.d(t,{i:function(){return x}});var l=a(689),r=a(9923),o=a(2886),i=a(9262),c=a(2542),s=a(7018),n=a(9788),d=a(8184),u=a(3240),m=a(4663),p=a(7664),h=a(4994);const g=(0,h.jB)({color:String,...(0,r.r)(),...(0,i.u)(),...(0,c.X)(),...(0,s.s)(),...(0,n.M)(),...(0,d.S)(),...(0,u.S)(),...(0,m.X)(),...(0,p.yx)()},"VSheet"),x=(0,h.RW)()({name:"VSheet",props:g(),setup(e,t){let{slots:a}=t;const{themeClasses:i}=(0,p.NX)(e),{backgroundColorClasses:m,backgroundColorStyles:g}=(0,o.z6)((0,l.toRef)(e,"color")),{borderClasses:x}=(0,r.M)(e),{dimensionStyles:f}=(0,c.S)(e),{elevationClasses:V}=(0,s.j)(e),{locationStyles:N}=(0,n.z)(e),{positionClasses:v}=(0,d.J)(e),{roundedClasses:w}=(0,u.v)(e);return(0,h.Ci)((()=>(0,l.createVNode)(e.tag,{class:["v-sheet",i.value,m.value,x.value,V.value,v.value,w.value,e.class],style:[g.value,f.value,N.value,e.style]},a))),{}}})}}]);
//# sourceMappingURL=200.ea56080b.js.map