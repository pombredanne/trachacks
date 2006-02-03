<?cs include "header.cs"?>
<?cs include "macros.cs"?>
<style type="text/css">
 input[type=password] { border: 1px solid #d7d7d7 }
 input[type=password] { padding: .25em .5em }
 input[type=password]:focus { border: 1px solid #886 }
 
 p.msg {color: red; font-weight: bold;}
</style>
<h2>Login</h2>
<p class="msg"><?cs var:auth.message ?></p>
  <form class="mod" id="modcomp" method="post">
   <table>
    <tr><td>Username:</td><td><input id="uid" name="uid" type="text"/></td></tr>
    <tr><td>Password:</td><td><input id="pwd" name="pwd" type="password"/></td></tr>
   </table>
   <div class="buttons">
    <input type="submit" name="login" value="Login" />
    <input type="submit" name="cancel" value="Cancel" />
   </div>
 </form>
<br />
<script type="text/javascript">
 var uid = document.getElementById("uid");
 uid.focus();
 uid.select();
</script> 
<?cs include:"footer.cs"?>
