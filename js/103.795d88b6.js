"use strict";(self["webpackChunkweekly_report"]=self["webpackChunkweekly_report"]||[]).push([[103],{6103:function(e,t,a){a.r(t),a.d(t,{default:function(){return Y}});a(4114);var l=a(689),r=a(2635),o=a(6945),c=a(4577),n=a(6863),i=a(2022),s=a(5350);const d={class:"rating-chart"};var u={__name:"RatingLineChart",props:{chartData:{type:Object,required:!0}},setup(e){const t=e,a=(0,l.ref)(null);let r=null;const o=e=>{const t=e.find((e=>"y1"===e.yAxisID));if(!t)return 3;const a=Math.ceil(Math.max(...t.data));return Math.max(3,a)},c=(0,l.computed)((()=>Math.max(1,Math.ceil(o.value/5)))),n={responsive:!0,maintainAspectRatio:!1,plugins:{legend:{position:"bottom"}},scales:{y:{type:"linear",position:"left",min:1,max:5,ticks:{stepSize:1,precision:0,callback:function(e){return Number.isInteger(e)?e:""}},title:{display:!0,text:"評価"}},y1:{type:"linear",position:"right",min:0,grid:{drawOnChartArea:!1},ticks:{stepSize:c.value,precision:0,callback:function(e){return e+"h"}},title:{display:!0,text:"残業時間"},afterDataLimits:e=>{e.max=o(t.chartData.datasets)}}}};return(0,l.onMounted)((()=>{a.value&&(r=new i.t1(a.value,{type:"line",data:t.chartData,options:n}))})),(0,l.watch)((()=>t.chartData),(e=>{r&&e&&(0,s.xT)({chart:r,chartData:e,isTop3:!1,options:n})}),{deep:!0}),(0,l.onBeforeUnmount)((()=>{r&&(r.destroy(),r=null)})),(e,t)=>((0,l.openBlock)(),(0,l.createElementBlock)("div",d,[(0,l.createElementVNode)("canvas",{ref_key:"chartRef",ref:a},null,512)]))}},m=a(6262);const p=(0,m.A)(u,[["__scopeId","data-v-d80d15a0"]]);var v=p,x=a(1059),k=a(9244),g=a(3725),h=a(3960),V=a(1652),f=a(8703),w=a(9663),y=a(9015),N=a(5741);const b={class:"d-flex align-center"},B={key:0,class:"d-flex align-center justify-center py-4"},C={key:0,class:"text-error"},_={key:1,class:"text-subtitle-1 text-medium-emphasis text-center py-4"},E={key:2,class:"px-4"},S={class:"text-body-1 px-1"},D={class:"text-subtitle-1 font-weight-medium mt-2 mb-1"},T={class:"flex-grow-1"},U={class:"text-subtitle-1 font-weight-medium mt-3 mb-1"},I={class:"flex-grow-1"};var A={__name:"ReportSummary",props:{memberUuid:{type:String,required:!0}},setup(e){const t=e,a=(0,l.ref)(!1),r=(0,l.ref)(null),o=(0,l.ref)(""),c=(0,l.ref)([]),n=async()=>{a.value=!0,r.value=null;try{const e=await(0,x.Sj)(t.memberUuid);o.value=e.summary,c.value=e.insights,o.value||c.value?.positive?.length||c.value?.negative?.length||(r.value="サマリーの生成に失敗しました")}catch(e){r.value=e.message||"サマリーの生成に失敗しました"}finally{a.value=!1}},i=e=>e?e.toFixed(0):"0",s=e=>e>=90?"error":"grey",d=(e,t=!1)=>t?e>=90?"非常に優れた成果です。継続して維持してください。":e>=70?"良好な成果が出ています。さらなる向上が期待できます。":e>=50?"一定の成果が出ています。":"小さな前進が見られます。":e>=90?"非常に重要な課題です。早急な対応が推奨されます。":e>=70?"重要な課題です。計画的な対応を検討してください。":e>=50?"要注意の課題です。状況を監視してください。":"参考程度の課題です。余裕があれば検討してください。";return(e,t)=>((0,l.openBlock)(),(0,l.createBlock)(g.Jn,{rounded:"lg"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(g.ri,{class:"d-flex align-center justify-space-between"},{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("div",b,[(0,l.createVNode)(f.wP,{icon:"mdi-magnify-scan",class:"mr-2"}),t[0]||(t[0]=(0,l.createTextVNode)(" 活動分析 "))]),(0,l.createVNode)(k.D,{disabled:a.value,color:"secondary",variant:"tonal",onClick:n},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(f.wP,{icon:"mdi-auto-fix",size:"20",class:"mr-1"}),(0,l.createTextVNode)(" "+(0,l.toDisplayString)(o.value?"再分析":"AI分析"),1)])),_:1},8,["disabled"])])),_:1}),(0,l.createVNode)(g.OQ,null,{default:(0,l.withCtx)((()=>[a.value?((0,l.openBlock)(),(0,l.createElementBlock)("div",B,[(0,l.createVNode)(y.x,{indeterminate:"",size:"42",width:"8",color:"secondary"})])):((0,l.openBlock)(),(0,l.createElementBlock)(l.Fragment,{key:1},[r.value?((0,l.openBlock)(),(0,l.createElementBlock)("div",C,(0,l.toDisplayString)(r.value),1)):o.value||c.value.length?((0,l.openBlock)(),(0,l.createElementBlock)("div",E,[t[5]||(t[5]=(0,l.createElementVNode)("div",{class:"text-h6 mb-2"},"全体の要約",-1)),(0,l.createElementVNode)("p",S,(0,l.toDisplayString)(o.value),1),(0,l.createVNode)(V.G,{class:"my-4"}),c.value.positive.length?((0,l.openBlock)(),(0,l.createElementBlock)(l.Fragment,{key:0},[(0,l.createElementVNode)("div",D,[(0,l.createVNode)(f.wP,{color:"success",class:"mr-1"},{default:(0,l.withCtx)((()=>t[1]||(t[1]=[(0,l.createTextVNode)("mdi-check-circle")]))),_:1}),t[2]||(t[2]=(0,l.createTextVNode)(" 良好な点 "))]),(0,l.createVNode)(w.x8,{density:"compact",class:"pt-0"},{default:(0,l.withCtx)((()=>[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(c.value.positive,((e,t)=>((0,l.openBlock)(),(0,l.createBlock)(w.gc,{key:"p"+t,class:"px-2 py-1"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(w.UZ,{class:"text-wrap d-flex align-center"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(f.wP,{icon:"mdi-circle-small"}),(0,l.createElementVNode)("span",T,(0,l.toDisplayString)(e.text),1),(0,l.withDirectives)(((0,l.openBlock)(),(0,l.createBlock)(h.x,{color:s(e.score),class:"ml-2"},{default:(0,l.withCtx)((()=>[(0,l.createTextVNode)((0,l.toDisplayString)(i(e.score)),1)])),_:2},1032,["color"])),[[N.m_,d(e.score,!0),"top"]])])),_:2},1024)])),_:2},1024)))),128))])),_:1})],64)):(0,l.createCommentVNode)("",!0),c.value.negative.length?((0,l.openBlock)(),(0,l.createElementBlock)(l.Fragment,{key:1},[(0,l.createElementVNode)("div",U,[(0,l.createVNode)(f.wP,{color:"warning",class:"mr-1"},{default:(0,l.withCtx)((()=>t[3]||(t[3]=[(0,l.createTextVNode)("mdi-alert")]))),_:1}),t[4]||(t[4]=(0,l.createTextVNode)(" 注意点・課題 "))]),(0,l.createVNode)(w.x8,{density:"compact",class:"pt-0"},{default:(0,l.withCtx)((()=>[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(c.value.negative,((e,t)=>((0,l.openBlock)(),(0,l.createBlock)(w.gc,{key:"n"+t,class:"px-2 py-1"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(w.UZ,{class:"text-wrap d-flex align-center"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(f.wP,{icon:"mdi-circle-small"}),(0,l.createElementVNode)("span",I,(0,l.toDisplayString)(e.text),1),(0,l.withDirectives)(((0,l.openBlock)(),(0,l.createBlock)(h.x,{color:s(e.score),class:"ml-2"},{default:(0,l.withCtx)((()=>[(0,l.createTextVNode)((0,l.toDisplayString)(i(e.score)),1)])),_:2},1032,["color"])),[[N.m_,d(e.score,!1),"top"]])])),_:2},1024)])),_:2},1024)))),128))])),_:1})],64)):(0,l.createCommentVNode)("",!0)])):((0,l.openBlock)(),(0,l.createElementBlock)("div",_," ボタンをクリックして分析レポートを生成してください "))],64))])),_:1})])),_:1}))}};const F=(0,m.A)(A,[["__scopeId","data-v-7351afb4"]]);var L=F,P=a(9660),M=a(9494),j=a(1982),J=a(3527),O=a(3630);const z={class:"d-flex align-center mb-4"},H={key:0},R={class:"text-h6"},Z={class:"text-h6"},q={class:"text-body-2 text-medium-emphasis"},Q={class:"text-h6"},W={class:"text-h6"},G={class:"work-items-list"},X={key:0,class:"mt-4"};var $={__name:"MemberReports",props:{memberUuid:{type:String,required:!0}},setup(e){const t=e,{getWeekJpText:a,getCurrentWeekString:i}=(0,r._)(),s=(0,l.ref)(""),d=(0,l.ref)([]),u=(0,l.ref)(null),m=e=>{const t=d.value.findIndex((t=>t.weekString===e));return a(-(5-t))},p=async()=>{try{const[e,a,l]=await Promise.all([(0,c.Xf)(t.memberUuid),(0,o.gc)(t.memberUuid),(0,o.ly)(t.memberUuid,i())]);e&&(s.value=e.name),d.value=a.map((e=>({weekString:e.weekString,report:e}))),l&&d.value.push({weekString:l.weekString,report:l}),u.value=d.value[d.value.length-1].weekString}catch(e){}},x=(0,l.computed)((()=>d.value.filter((e=>"none"!==e.report?.status)).length)),h=(0,l.computed)((()=>{const e=d.value.map(((e,t)=>a(-(5-t))));return{labels:e,datasets:[{label:"ストレス度",data:d.value.map((e=>"none"===e.report?.status?null:e.report?.rating?.stress||null)),borderColor:"rgb(192, 75, 192)",backgroundColor:"rgba(192, 75, 192, 0.2)",fill:!0,yAxisID:"y"},{label:"タスク達成度",data:d.value.map((e=>"none"===e.report?.status?null:e.report?.rating?.achievement||null)),borderColor:"rgb(75, 192, 192)",backgroundColor:"rgba(75, 192, 192, 0.2)",fill:!0,yAxisID:"y"},{label:"タスク難易度",data:d.value.map((e=>"none"===e.report?.status?null:e.report?.rating?.disability||null)),borderColor:"rgb(255, 99, 132)",backgroundColor:"rgba(255, 99, 132, 0.2)",fill:!0,yAxisID:"y"},{label:"残業時間",data:d.value.map((e=>"none"===e.report?.status?null:e.report?.overtimeHours??null)),borderColor:"rgb(54, 162, 235)",borderDash:[5,3],backgroundColor:"rgba(54, 162, 235, 0.2)",fill:!1,yAxisID:"y1"}]}})),V=(0,l.computed)((()=>d.value[0]?.weekString)),y=(0,l.computed)((()=>d.value[d.value.length-1]?.weekString)),N=(0,l.computed)((()=>d.value.length)),b=(0,l.computed)((()=>d.value.filter((e=>"none"!==e.report?.status)).length)),B=(0,l.computed)((()=>{const e=d.value.filter((e=>"none"!==e.report?.status&&"number"===typeof e.report.overtimeHours));return e.length?e.reduce(((e,t)=>e+t.report.overtimeHours),0)/e.length:0})),C=(0,l.computed)((()=>{const e={};return d.value.forEach((t=>{t.report?.projects?.forEach((t=>{e[t.name]=(e[t.name]||0)+1}))})),Object.entries(e).sort((([,e],[,t])=>t-e))[0]?.[0]}));return(0,l.onMounted)(p),(e,a)=>((0,l.openBlock)(),(0,l.createBlock)(M.IZ,null,{default:(0,l.withCtx)((()=>[(0,l.createVNode)(M.Li,null,{default:(0,l.withCtx)((()=>[(0,l.createVNode)(M.B6,null,{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("div",z,[(0,l.createVNode)(k.D,{icon:"mdi-arrow-left",variant:"tonal",class:"ml-n16 mr-4",onClick:a[0]||(a[0]=t=>e.$router.back())}),(0,l.createElementVNode)("h3",null,[(0,l.createVNode)(f.wP,{size:"large",class:"mr-1"},{default:(0,l.withCtx)((()=>a[3]||(a[3]=[(0,l.createTextVNode)(" mdi-calendar-range ")]))),_:1}),a[4]||(a[4]=(0,l.createTextVNode)(" 週次報告履歴")),s.value?((0,l.openBlock)(),(0,l.createElementBlock)("span",H,"（"+(0,l.toDisplayString)(s.value)+"さん）",1)):(0,l.createCommentVNode)("",!0)])]),(0,l.createVNode)(g.Jn,{class:"mb-4",rounded:"lg"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(g.ri,null,{default:(0,l.withCtx)((()=>[(0,l.createVNode)(f.wP,{icon:"mdi-calendar-text-outline",class:"mr-1"}),a[5]||(a[5]=(0,l.createTextVNode)(" 期間の概要 "))])),_:1}),N.value?((0,l.openBlock)(),(0,l.createBlock)(g.OQ,{key:0,class:"px-6"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(M.Li,null,{default:(0,l.withCtx)((()=>[(0,l.createVNode)(M.B6,{cols:"12",sm:"6",md:"3"},{default:(0,l.withCtx)((()=>[a[6]||(a[6]=(0,l.createElementVNode)("div",{class:"text-subtitle-2 mb-1"},"対象期間",-1)),(0,l.createElementVNode)("div",R,(0,l.toDisplayString)(m(V.value))+" 〜 "+(0,l.toDisplayString)(m(y.value)),1)])),_:1}),(0,l.createVNode)(M.B6,{cols:"12",sm:"6",md:"2"},{default:(0,l.withCtx)((()=>[a[7]||(a[7]=(0,l.createElementVNode)("div",{class:"text-subtitle-2 mb-1"},"報告提出率",-1)),(0,l.createElementVNode)("div",Z,[(0,l.createTextVNode)((0,l.toDisplayString)(Math.round(b.value/N.value*100))+"% ",1),(0,l.createElementVNode)("span",q," ("+(0,l.toDisplayString)(b.value)+"/"+(0,l.toDisplayString)(N.value)+"週) ",1)])])),_:1}),(0,l.createVNode)(M.B6,{cols:"12",sm:"6",md:"2"},{default:(0,l.withCtx)((()=>[a[9]||(a[9]=(0,l.createElementVNode)("div",{class:"text-subtitle-2 mb-1"},"平均残業時間",-1)),(0,l.createElementVNode)("div",Q,[(0,l.createTextVNode)((0,l.toDisplayString)(B.value.toFixed(1))+" ",1),a[8]||(a[8]=(0,l.createElementVNode)("span",{class:"text-body-2"},"時間/週",-1))])])),_:1}),(0,l.createVNode)(M.B6,{cols:"12",sm:"6",md:"5"},{default:(0,l.withCtx)((()=>[a[10]||(a[10]=(0,l.createElementVNode)("div",{class:"text-subtitle-2 mb-1"},"最頻プロジェクト",-1)),(0,l.createElementVNode)("div",W,(0,l.toDisplayString)(C.value||"該当なし"),1)])),_:1})])),_:1})])),_:1})):(0,l.createCommentVNode)("",!0)])),_:1}),x.value>0?((0,l.openBlock)(),(0,l.createBlock)(L,{key:0,"member-uuid":t.memberUuid,class:"mb-4"},null,8,["member-uuid"])):(0,l.createCommentVNode)("",!0),x.value>0?((0,l.openBlock)(),(0,l.createBlock)(g.Jn,{key:1,class:"my-4",rounded:"lg"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(g.ri,null,{default:(0,l.withCtx)((()=>[(0,l.createVNode)(f.wP,{icon:"mdi-chart-line",class:"mr-1"}),a[11]||(a[11]=(0,l.createTextVNode)(" 評価・残業時間推移 "))])),_:1}),(0,l.createVNode)(g.OQ,null,{default:(0,l.withCtx)((()=>[(0,l.createVNode)(v,{"chart-data":h.value,class:"mt-2"},null,8,["chart-data"])])),_:1})])),_:1})):(0,l.createCommentVNode)("",!0),(0,l.createVNode)(j.hM,{modelValue:u.value,"onUpdate:modelValue":a[1]||(a[1]=e=>u.value=e),class:"mb-4"},{default:(0,l.withCtx)((()=>[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(d.value,(e=>((0,l.openBlock)(),(0,l.createBlock)(j.U7,{key:e.weekString,value:e.weekString,class:"text-body-1"},{default:(0,l.withCtx)((()=>[(0,l.createTextVNode)((0,l.toDisplayString)(m(e.weekString)),1)])),_:2},1032,["value"])))),128))])),_:1},8,["modelValue"]),(0,l.createVNode)(O.r,{modelValue:u.value,"onUpdate:modelValue":a[2]||(a[2]=e=>u.value=e),class:"elevation-4 rounded-lg"},{default:(0,l.withCtx)((()=>[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(d.value,(e=>((0,l.openBlock)(),(0,l.createBlock)(O.m,{key:e.weekString,value:e.weekString},{default:(0,l.withCtx)((()=>[e.report?((0,l.openBlock)(),(0,l.createBlock)(g.Jn,{key:0,class:"pa-4"},{default:(0,l.withCtx)((()=>["none"!==e.report.status?((0,l.openBlock)(),(0,l.createBlock)(M.Li,{key:0},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(M.B6,{cols:"12",md:"5"},{default:(0,l.withCtx)((()=>[a[13]||(a[13]=(0,l.createElementVNode)("div",{class:"text-subtitle-1 font-weight-medium mb-2"},"作業内容",-1)),(0,l.createVNode)(w.x8,{dense:"",class:"bg-transparent pa-0"},{default:(0,l.withCtx)((()=>[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(e.report.projects,((e,t)=>((0,l.openBlock)(),(0,l.createBlock)(w.gc,{key:t,class:"px-2 py-1"},{default:(0,l.withCtx)((()=>[(0,l.createVNode)(w.UZ,null,{default:(0,l.withCtx)((()=>[(0,l.createVNode)(f.wP,{small:""},{default:(0,l.withCtx)((()=>a[12]||(a[12]=[(0,l.createTextVNode)("mdi-folder-outline")]))),_:1}),(0,l.createTextVNode)(" "+(0,l.toDisplayString)(e.name),1)])),_:2},1024),(0,l.createVNode)(w.w,{class:"ml-6"},{default:(0,l.withCtx)((()=>[(0,l.createElementVNode)("ul",G,[((0,l.openBlock)(!0),(0,l.createElementBlock)(l.Fragment,null,(0,l.renderList)(e.workItems,((e,t)=>((0,l.openBlock)(),(0,l.createElementBlock)("li",{key:t},(0,l.toDisplayString)(e.content),1)))),128))])])),_:2},1024)])),_:2},1024)))),128))])),_:2},1024),e.report.overtimeHours>=0?((0,l.openBlock)(),(0,l.createElementBlock)("div",X,[(0,l.createVNode)(n.A,{"overtime-hours":e.report.overtimeHours},null,8,["overtime-hours"])])):(0,l.createCommentVNode)("",!0)])),_:2},1024),(0,l.createVNode)(M.B6,{cols:"12",md:"7"},{default:(0,l.withCtx)((()=>[a[14]||(a[14]=(0,l.createElementVNode)("div",{class:"text-subtitle-1 font-weight-medium mb-1"}," 振り返り（成果と課題） ",-1)),(0,l.createVNode)(J.J,{modelValue:e.report.issues,"onUpdate:modelValue":t=>e.report.issues=t,readonly:"","auto-grow":"",rows:"2","hide-details":"",variant:"outlined",class:"small-text-area mb-4"},null,8,["modelValue","onUpdate:modelValue"]),a[15]||(a[15]=(0,l.createElementVNode)("div",{class:"text-subtitle-1 font-weight-medium mb-1"}," 次の目標、改善施策 ",-1)),(0,l.createVNode)(J.J,{modelValue:e.report.improvements,"onUpdate:modelValue":t=>e.report.improvements=t,readonly:"","auto-grow":"",rows:"2","hide-details":"",variant:"outlined",class:"small-text-area mb-2"},null,8,["modelValue","onUpdate:modelValue"])])),_:2},1024)])),_:2},1024)):((0,l.openBlock)(),(0,l.createBlock)(P.l,{key:1,type:"info",variant:"tonal"},{default:(0,l.withCtx)((()=>a[16]||(a[16]=[(0,l.createTextVNode)(" この週の報告はありません ")]))),_:1}))])),_:2},1024)):(0,l.createCommentVNode)("",!0)])),_:2},1032,["value"])))),128))])),_:1},8,["modelValue"])])),_:1})])),_:1})])),_:1}))}};const K=(0,m.A)($,[["__scopeId","data-v-4ea12dae"]]);var Y=K},3630:function(e,t,a){a.d(t,{m:function(){return r.m},r:function(){return l.r3}});var l=a(6048),r=a(1781)}}]);
//# sourceMappingURL=103.795d88b6.js.map