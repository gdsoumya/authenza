document.getElementById('login-form').addEventListener('submit',function(e){
	e.preventDefault();
	
	//const formdata1 = new FormData();
	let data1= new FormData();
    const name2 = document.getElementById('your_email').value;
    //const name1=document.getElementById('your_pass').value;
 const api_key="a93e8f09748d43f3a44571f2893d5c2b";
    const client_id="6329761b61bf4e569217c946fc3c0392";
    //const token = localStorage.getItem('user_login_token');
    email_verify(api_key,client_id,name2);
                    
	
});


function email_verify(api_key,client_id,name2){  
    var json_data_user_email_verify = {
        "api_key":api_key,
		"client_id":client_id,
        "email":name2 
    };

var data_user_email_verify = JSON.stringify(json_data_user_email_verify);
console.log(data_user_email_verify);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/user/init_email_verify";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");

//xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        console.log(json);
alert("email sent-check inbox")
        window.location="./Email_verify3.html";
}else{
    console.log("aadada");
}  
}
xhr.send(data_user_email_verify);
}


