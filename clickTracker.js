/* failed try to import jquery in js file  */
//var script = document.createElement('script');
//script.src = 'http://code.jquery.com/jquery-1.11.3.min.js';
//script.type = 'text/javascript';
//document.getElementsByTagName('head')[0].appendChild(script);

// need to check version and collision of jquery on target web service

// version 0.1
var serverUrl = 'http://{{service-name}}-{{eb_version_lable_suffix}}.elasticbeanstalk.com'; // input your settinged RESTful API Server info
var token = "ACdzNVRsRlZVa1JLAU4WFKVsVk9WVk5ET1F1PB==";  // hard coded temporary service token for olley
var loaded = Date.now();

function initQueue(){
	// LocalStorage 지원여부 체크 및 기존에 저장된 큐가 있다면 가져오기
	if(typeof(Storage) !== "undefined") {
		var LocalLogQueue = JSON.parse(localStorage.getItem("LocalLogQueue"));
	} else {
		console.log("Local Storage not support");
		return false;
	}
	console.log("initQueue 1");
	console.log(LocalLogQueue);
	// 위에서 가져와진 큐가 존재하는지 체크, 없다면 새로 생성하여 localStorage에 초기화
	if(LocalLogQueue === null || LocalLogQueue === ""){
		var LocalLogQueue = [];
		console.log("initQueue 2");
		console.log(LocalLogQueue);
		localStorage.setItem("LocalLogQueue", JSON.stringify(LocalLogQueue));
	}
}

function pushQueue(json_data){
	var LocalLogQueue = JSON.parse(localStorage.getItem("LocalLogQueue"));
	if(LocalLogQueue === null || LocalLogQueue === ""){
		initQueue();
		return addQueue(json_data);
	}
	LocalLogQueue.push(json_data);
	localStorage.setItem("LocalLogQueue", JSON.stringify(LocalLogQueue));
	console.log("addQueue 3");
	console.log(LocalLogQueue);
	return true;
}

function popQueue(){
	var LocalLogQueue = JSON.parse(localStorage.getItem("LocalLogQueue"));
	if(LocalLogQueue === null || LocalLogQueue === ""){
		initQueue();
		console.log("popQueue, empty, init");
		return false;
	}
	else{
		var json_data = LocalLogQueue.pop();
		localStorage.setItem("LocalLogQueue", JSON.stringify(LocalLogQueue));
		console.log("popQueue 2");
		// console.log(LocalLogQueue);
		if(typeof(json_data) == "undefined"){
			return false;
		}
		else{
			return json_data;
		}
	}
}

function shiftQueue(){
	var LocalLogQueue = JSON.parse(localStorage.getItem("LocalLogQueue"));
	if(LocalLogQueue === null || LocalLogQueue === ""){
		initQueue();
		console.log("popQueue, empty, init");
		return false;
	}
	else{
		var json_data = LocalLogQueue.shift();
		localStorage.setItem("LocalLogQueue", JSON.stringify(LocalLogQueue));
		console.log("popQueue 2");
		// console.log(LocalLogQueue);
		if(typeof(json_data) == "undefined"){
			return false;
		}
		else{
			return json_data;
		}
	}
}

function getAllQueue(){
	var LocalLogQueue = JSON.parse(localStorage.getItem("LocalLogQueue"));
	console.log("getAllQueue 1");
	console.log(LocalLogQueue);
	if(LocalLogQueue === null || LocalLogQueue === ""){
		initQueue();
		console.log("getAllQueue, empty, init");
		return false;
	}
	else{
		while(true){
			var json_data = popQueue();
			if(json_data){
				console.log(json_data);
			}
			else{
				console.log("getAllQueue, empty");
				break;
			}
		}
	}
	return true;
}

function isEmptyQueue(){
	var LocalLogQueue = JSON.parse(localStorage.getItem("LocalLogQueue"));
	if(LocalLogQueue === null || LocalLogQueue === ""){
		initQueue();
		console.log("checkEmptyQueue, empty, init");
		return true;
	}
	else{
		console.log("checkEmptyQueue, queue length:");
		console.log(LocalLogQueue.length);
		if(LocalLogQueue.length == 0){
			return true;
		}
		else{
			return false;
		}
	}
}

// for make user_key , len == 20
function make_random_key()
{
	var text = "";
	var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

	for( var i=0; i < 20; i++ )
		text += possible.charAt(Math.floor(Math.random() * possible.length));

	return text;
}

function clickHandleEvent(e){
	var evt = e ? e:window.event;
	var clickX=0, clickY=0;

	if ((evt.clientX || evt.clientY) &&
		document.body &&
		document.body.scrollLeft!=null) {
		clickX = evt.clientX + document.body.scrollLeft;
		clickY = evt.clientY + document.body.scrollTop;
	}
	if ((evt.clientX || evt.clientY) &&
		document.compatMode=='CSS1Compat' &&
		document.documentElement &&
		document.documentElement.scrollLeft!=null) {
		clickX = evt.clientX + document.documentElement.scrollLeft;
		clickY = evt.clientY + document.documentElement.scrollTop;
	}
	if (evt.pageX || evt.pageY) {
		clickX = evt.pageX;
		clickY = evt.pageY;
	}
	var click_data = {
		pageX : clickX,
		pageY : clickY,
		clientX : evt.clientX,
		clientY : evt.clientY,
		screenX : evt.screenX,
		screenY : evt.screenY
	}
	return click_data
}

function makeLog(e, link, init){
	console.log("make log 1");
	init = typeof init !== 'undefined' ? init : false;
	stored_link = link;
	if(link == undefined || link === true || link === false ){
		link = "";
	}
	var spent_milli_sec = Date.now() - loaded;
	var load_count = Number(localStorage.getItem("load_count"));
	load_count += 1;
	localStorage.setItem("load_count", load_count);
	click_data = clickHandleEvent(e);
	// var data= 'link=' + $(this).attr("href") + '&spent_milli_sec=' + spent_milli_sec + '&timestamp=' + Date.now()
	var now_ISO = new Date().toISOString();
	var json_data = {
		timestamp: now_ISO,
		token: token,
		user_key: localStorage.getItem("user_key"),
		current_page: document.location.href,
		link: link,
		x : click_data["pageX"],
		y : click_data["pageY"],
		spent_milli_sec: spent_milli_sec,
		user_agent : navigator.userAgent,
		load_count:load_count
	}
	if ( init == true ){
		initQueue();
		pushQueue(json_data);
		return;
	}
	pushQueue(json_data);
	console.log("make log 2");
}

function sendAllLog(tmpLink){
	if(typeof(tmpLink) == "undefined" || tmpLink == null){
		tmpLink = "sendAllLog";
	}
	else{
		tmpLink = tmpLink+" _ sendAllLog";
	}
	//flush queue
	var LocalLogQueue = JSON.parse(localStorage.getItem("LocalLogQueue"));
	console.log("sendAllLog flush queue 1");
	console.log(LocalLogQueue);
	if(LocalLogQueue === null || LocalLogQueue === ""){
		initQueue();
		console.log("sendAllLog flush queue, empty, init");
		return false;
	}
	else{
		var logCount = LocalLogQueue.length;
		console.log("logCount "+logCount);
		while(logCount >= 1){
			console.log("flusing "+logCount);
			// do not flush, only send
			sendLog(link=tmpLink,flush=false);
			logCount--;
		}
	}
}

function sendLog(link, flush){
	stored_link = link;
	if(typeof(link) == "undefined" || link == null){
		link = "";
	}
	if(typeof(link) == "undefined" || link == null){
		flush = false;
	}
	console.log("send log");

	var json_data = popQueue();
	if(!json_data){
		console.log("log init");
		makeLog(link=document.location.href, init=true);
		// check below line
		sendLog(link=document.location.href);
	}
	if(!json_data["link"]){
		json_data["link"] = link;
	}else{
		console.log("sendLog aleady json link");
		console.log(json_data["link"]);
	}
	console.log(json_data);
	if(link != ""){
		$.ajax({
			type: "post",
			dataType: 'json',
			url: serverUrl,
			data: json_data,
			success : function(){
				console.log("success");
			},
			complete: function(){
				console.log("complete");
			},
			error : function(xhr, status, error) {
				console.log("error");
			}
		});
	}
	else{
		console.log("fail sending");
	}

	// check flush queue or not
	if(flush){
		sendAllLog(link);
	}

}

$(document).ready(function() {
	// init local storage
	if (typeof(Storage) !== "undefined") {

		load_count = Number(localStorage.getItem("load_count"));
		user_key = localStorage.getItem("user_key");

		if ( load_count === 0 ){
			load_count = 0;
			localStorage.setItem("load_count", load_count);
		}
		if ( user_key === null ){
			console.log("make_key");
			var user_key = make_random_key();
			localStorage.setItem("user_key", user_key);
		}

		console.log(load_count);
		console.log(user_key);
		load_count += 1;
		localStorage.setItem("load_count", load_count);

		if(isEmptyQueue()){
			makeLog(link=document.location.href, init=true);
		}
		// init, send visit log
		sendLog(link=document.location.href,flush=true);

	} else {
		console.log("not support");
	}
});


function tagClickListner(event, arg_this, tag) {
	console.log("DOMListner tag " + tag);
	if (Number(Date.now() - oldTime_click) > click_listen_milli_sec_threshold) {

		var tagClass = String($(arg_this).attr("class"));
		tagClass = tagClass !== 'undefined' ? tagClass : "";

		var tagId = String($(arg_this).attr("id"));
		tagId = tagId !== 'undefined' ? tagId : "";

		var tagName = String($(arg_this).attr("name"));
		tagName = tagName !== 'undefined' ? tagName : "";

		// var tagReactid = String($(arg_this).attr("reactid"));
		// tagReactid = tagReactid !== 'undefined' ? tagReactid : "";

		var tagDataReactid = String($(arg_this).attr("data-reactid"));
		tagDataReactid = tagDataReactid !== 'undefined' ? tagDataReactid : "";

		var s = ";";
		tagInfo = tag + s + tagClass + s + tagId + s + tagName + s + tagDataReactid;

		if ($(arg_this).attr("href")) {
			console.log("DOMListner attribute href");
			makeLog(e = window.event, link = $(arg_this).attr("href"), init = false);
		}
		else if ($(arg_this).attr("data-reactid") || $(arg_this).attr("reactid")) {
			console.log("DOMListner attribute reactids");
			makeLog(e = window.event, link = tagInfo, init = false);
		}
		else{
			console.log("DOMListner attribute else");
			console.log(tagInfo);
			makeLog(e = window.event, link = tagInfo, init = false);
		}
	}
	oldTime_click = Date.now();
}


// click event listener
var oldTime_click = Date.now();
var click_listen_milli_sec_threshold = 100;
$(document).bind('DOMSubtreeModified', function() {
	// click event listener
	$('a').click(function(e) {
		tagClickListner(window.event, this, 'a');
	});
	$('span').click(function(e) {
		tagClickListner(window.event, this, 'span');
	});
	$('button').click(function(e) {
		tagClickListner(window.event, this, 'button');
	});
	$('input').click(function(e) {
		tagClickListner(window.event, this, 'input');
	});
});

// url change listener
var urlTracker = document.location.href;
var oldTime = Date.now();
var url_change_milli_sec_threshold = 1000;
$(document).bind('DOMSubtreeModified', function() {
	if(document.location.href != urlTracker) {
		currentTime = Date.now();
		if((Number(currentTime - oldTime)) > url_change_milli_sec_threshold) {
			console.log("page modified!");
			console.log(urlTracker);
			console.log(document.location.href);
			sendLog(link=document.location.href, flush=true);
		}
		oldTime = Date.now();
	}
	else{
		currentTime = Date.now();
		if((Number(currentTime - oldTime)) > url_change_milli_sec_threshold) {
			console.log("single page DOMSubtreeModified");
			console.log(urlTracker);
			sendLog(link=document.location.href, flush=true);
		}
		oldTime = Date.now();
	}
});
