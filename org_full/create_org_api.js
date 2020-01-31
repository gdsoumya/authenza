document.getElementById('myform').addEventListener('submit',function(e){
	e.preventDefault();
	console.log("Hello");
	//const formdata1 = new FormData();
    const name2 = document.getElementById('textarea').value;
    const api_key="74d9c3f6bb384d168b658069e3c1825a";
	const client_id="8ab95867280c41cdbfe1cfb9db7d16db";
	

   //  window.localStorage.setItem('api_key',api_key);
   //  window.localStorage.setItem('client_id',client_id);
   // window.localStorage.setItem('user_name', name1);
   //  window.localStorage.setItem('user_email', name2);
   //  window.localStorage.setItem('user_password', password2);

    create_api(name2);
	});


function create_api(name2){  
    var token=window.localStorage.getItem('org_token');
    console.log(token, "HELLOOO")
    var json_data_user_register = {
        "description":name2,
        "token":token
    };
var data_user_register = JSON.stringify(json_data_user_register);
console.log(data_user_register);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/org/create_api_key";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        alert("API CREATED");
        
        //hideLoader();
        }
}   
xhr.send(data_user_register);
}