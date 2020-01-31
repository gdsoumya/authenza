
document.getElementById('login-form').addEventListener('submit',function(e){
	e.preventDefault();
	
	//const formdata1 = new FormData();
	let data1= new FormData();
    const name2 = document.getElementById('your_email').value;
    //const name1=document.getElementById('your_pass').value;
    const password2 = document.getElementById('your_pass').value;
    const api_key="74d9c3f6bb384d168b658069e3c1825a";
	const client_id="8ab95867280c41cdbfe1cfb9db7d16db";

    user_login(api_key,client_id,name2,password2);
                    
	
});


function user_login(api_key,client_id,name2,password){  
    var json_data_user_login = {
        "api_key":api_key,
		"client_id":client_id,
		"email":name2,
        "password":password
    };
var data_user_login = JSON.stringify(json_data_user_login);
console.log(data_user_login);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/user/login";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        window.token = json['token'];
        console.log(json);
        window.localStorage.setItem('user_login_token',json.token);        
        //alert(json.token);
        window.location="../../index_dash.html";
        //hideLoader();
        }
}   
xhr.send(data_user_login);
}