window.onload=function(){
        var mb = document.getElementById("b1");
        var cl = document.getElementById("cl");
        cl.addEventListener("click", handler2);
    }


    function handler() {
      document.querySelector('.modal').style.display="flex";
    }

    function handler2() {
        user_two_factor_cancel_reg()
      document.querySelector('.modal').style.display="none";
    }

function user_two_factor_enable(){

    const api_key="74d9c3f6bb384d168b658069e3c1825a";
    const client_id="8ab95867280c41cdbfe1cfb9db7d16db";
    const token = window.localStorage.getItem('user_login_token');
    
    var json_data_user_two_factor_enable = {   
        "client_id": client_id,
        "api_key": api_key,
        "token": token
    };
var data_user_two_factor_enable = JSON.stringify(json_data_user_two_factor_enable);
console.log(data_user_two_factor_enable);
// showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/user/two_factor/enable";
xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader("Access-Control-Allow-Origin","*");
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        if(xhr.status == 200){
            console.log(json['qr']);
            var url = "http://52.203.240.40:8080"+json['qr'];
            document.getElementById("qrcode").setAttribute('src',url);
            handler();
            user_two_factor_active_check(api_key,client_id,token);  
        }else{
            console.log(json);
            alert("Already Enabled");
        }
        }
}   
xhr.send(data_user_two_factor_enable);
}

function user_two_factor_active_check(apikey,clientid,token){

var json_data_user_two_factor_active_check= {
        "api_key": apikey,
        "client_id": clientid,
        "token": token
    };
var data_user_two_factor_active_check = JSON.stringify(json_data_user_two_factor_active_check);

xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/user/two_factor/active_check";
xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader("Access-Control-Allow-Origin","*");
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        console.log(json);
        if(xhr.status == 200 && json['two_factor']){
            handler2();
            alert("2FA Activated")
        }else{
            console.log(json);
            setTimeout(user_two_factor_active_check(apikey,clientid,token), 5000);
        }
        }
}   
xhr.send(data_user_two_factor_active_check);
}


function user_two_factor_cancel_reg(){
    const api_key="74d9c3f6bb384d168b658069e3c1825a";
    const client_id="8ab95867280c41cdbfe1cfb9db7d16db";
    const token = window.localStorage.getItem('user_login_token');
var json_data_user_two_cancel_reg = {
    "api_key": api_key,
    "client_id": client_id,
    "token":token
};
var data_user_two_cancel_reg = JSON.stringify(json_data_user_two_cancel_reg);

xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/user/two_factor/cancel_reg";
xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader("Access-Control-Allow-Origin","*");
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        if(xhr.status == 200){
        console.log(json);
        }
        }
}   
xhr.send(data_user_two_cancel_reg);
}
