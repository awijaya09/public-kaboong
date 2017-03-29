
window.fbAsyncInit = function() {
  FB.init({
    appId      : '272614203189263',
    cookie     : true,
    xfbml      : true,
    version    : 'v2.8'
  });
  FB.AppEvents.logPageView();
};

(function(d, s, id){
 var js, fjs = d.getElementsByTagName(s)[0];
 if (d.getElementById(id)) {return;}
 js = d.createElement(s); js.id = id;
 js.src = "//connect.facebook.net/en_US/sdk.js";
 fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function sendTokenToServer() {
  var access_token = FB.getAuthResponse()['accessToken'];
  FB.api('/me', function(response){
    console.log('Succesful login for: ' + response.name)
    $.ajax{
      type: 'POST',
      url: '/fbconnect?state={{STATE}}',
      processData: false,
      data: access_token,
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {
        if (result) {
          $('#result').html('Login successful, redirecting');
          setTimeout(function(){
            window.location.href = "/";
          }, 4000);
        } else {
          $('#result').html('Failed to make server request!');
        }
      }
    }
  });

}