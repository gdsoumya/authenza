const form = document.getElementById('form');

form.addEventListener('submit',function(e){
	e.preventDefault();

    const formdata = new FormData();
    let data= new FormData();
	  const input = document.getElementById('logo');
    const name1 = document.getElementById('uname').value;
    const email1 = document.getElementById('email').value;
    const password1 = document.getElementById('password').value;

    data.append("image",input[0]);
    data.append("email",email1);
    data.append("name",name1);
    data.append("password",password1);



    var json;
    fetch('http://52.203.240.40:8080/org/register', { // Your POST endpoint
    method: 'POST',
    mode:'cors',
    body: data // This is your file object
  }).then(
    response => response.json() // if the response is a JSON object
  ).then(
    success => swal({
        title: "SUCCESS",
        
  text: "SUCCESSFULL REGISTER-THANK YOU FOR TRUSTING AUTHENZA!",
})
    //alert("SUCCESFULLY REGISTERED ORGANISATION = " +  name1) // Handle the success response object
  ).catch(
    error => console.log(error) // Handle the error response object
  ); 
// data.forEach((value,key) => {
// console.log(value)
//});
   
});
 