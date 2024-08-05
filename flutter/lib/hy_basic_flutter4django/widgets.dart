import 'package:flutter/material.dart';
import 'package:hy_basic_flutter4django/hy_basic_flutter4django/network.dart';

class LoginPage {
  static Widget getLoginWidget(
      BuildContext context, Function onLogin, Color buttonColor,
      {String? errortext}) {
    TextStyle loginTextStyle = TextStyle(fontFamily: 'Arial', fontSize: 20.0);

    TextEditingController userNameController = TextEditingController();
    final userNameField = TextField(
      controller: userNameController,
      obscureText: false,
      style: loginTextStyle,
      decoration: InputDecoration(
          contentPadding: EdgeInsets.fromLTRB(20.0, 15.0, 20.0, 15.0),
          hintText: "Username",
          border:
              OutlineInputBorder(borderRadius: BorderRadius.circular(32.0))),
    );

    TextEditingController passwordController = TextEditingController();
    final passwordField = TextField(
      controller: passwordController,
      obscureText: true,
      style: loginTextStyle,
      decoration: InputDecoration(
          contentPadding: EdgeInsets.fromLTRB(20.0, 15.0, 20.0, 15.0),
          hintText: "Password",
          border:
              OutlineInputBorder(borderRadius: BorderRadius.circular(32.0))),
    );

    final loginButton = Material(
      elevation: 5.0,
      borderRadius: BorderRadius.circular(30.0),
      color: buttonColor,
      child: MaterialButton(
        minWidth: MediaQuery.of(context).size.width,
        padding: EdgeInsets.fromLTRB(20.0, 15.0, 20.0, 15.0),
        onPressed: () async {
          String user = userNameController.text;
          String password = passwordController.text;
          var loginError = await WebSession.login(user, password);
          onLogin(loginError);
        },
        child: Text("Login",
            textAlign: TextAlign.center,
            style: loginTextStyle.copyWith(
                color: Colors.white, fontWeight: FontWeight.bold)),
      ),
    );

    return Scaffold(
        body: SingleChildScrollView(
      child: Center(
        child: Container(
          color: Colors.white,
          constraints: BoxConstraints(maxWidth: 400.0),
          child: Padding(
            padding: const EdgeInsets.all(36.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                SizedBox(height: 45.0),
                userNameField,
                SizedBox(height: 25.0),
                passwordField,
                SizedBox(height: 35.0),
                loginButton,
                SizedBox(height: 15.0),
                if (errortext != null)
                  // Show error message in selection color widget
                  Text(errortext,
                      style: TextStyle(
                          color: Colors.red,
                          fontSize: 20.0,
                          fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ),
      ),
    ));
  }
}
