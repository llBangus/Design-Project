import 'package:flutter/material.dart';
import 'package:mongo_dart/mongo_dart.dart' as mongo;
import 'dart:math';
import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dropbox',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.cyan,
        accentColor: Colors.cyanAccent,
        textTheme: TextTheme(
          bodyText2: TextStyle(color: Colors.cyanAccent),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(),
          enabledBorder: OutlineInputBorder(
            borderSide: BorderSide(color: Colors.cyanAccent),
          ),
          focusedBorder: OutlineInputBorder(
            borderSide: BorderSide(color: Colors.cyanAccent),
          ),
        ),
        buttonTheme: ButtonThemeData(
          buttonColor: Colors.cyan,
          textTheme: ButtonTextTheme.primary,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
        ),
      ),
      initialRoute: '/loginform',
      routes: {
        '/loginform': (context) => LoginForm(),
        '/register': (context) => RegistrationForm(),
        '/homescreen': (context) => HomeScreen(),
      },
      home: Scaffold(
        body: Container(
          child: LoginForm(),
        ),
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  void _generateOTP(BuildContext context, String username) async {
    final db = await mongo.Db.create(
        'mongodb+srv://pdipbox:projectdesign2@cluster0.jqevhad.mongodb.net/dropbox?retryWrites=true&w=majority');
    await db.open();
    final collection = db.collection('userinfo');
    final otp = _generateRandomOTP();
    await collection.updateOne(
      mongo.where.eq('User', username),
      mongo.modify.set('otp', otp),
    );
    await db.close();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('OTP Generated'),
        content: Text('Your OTP is: $otp'),
        actions: <Widget>[
          TextButton(
            child: Text('OK'),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }

  void _acceptRequest(BuildContext context, String username) async {
    final db = await mongo.Db.create(
        'mongodb+srv://pdipbox:projectdesign2@cluster0.jqevhad.mongodb.net/dropbox?retryWrites=true&w=majority');
    await db.open();
    final collection = db.collection('userinfo');
    await collection.update(
      mongo.where.eq('User', username),
      mongo.modify.set('request_status', 'accepted'),
    );
    await db.close();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Request Accepted'),
        content: Text('You accepted the request.'),
        actions: <Widget>[
          TextButton(
            child: Text('OK'),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }

  void _rejectRequest(BuildContext context, String username) async {
    final db = await mongo.Db.create(
        'mongodb+srv://pdipbox:projectdesign2@cluster0.jqevhad.mongodb.net/dropbox?retryWrites=true&w=majority');
    await db.open();
    final collection = db.collection('userinfo');
    await collection.update(
      mongo.where.eq('User', username),
      mongo.modify.set('request_status', 'rejected'),
    );
    await db.close();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Request Rejected'),
        content: Text('You rejected the request.'),
        actions: <Widget>[
          TextButton(
            child: Text('OK'),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }

  int _generateRandomOTP() {
    return 1000 + Random().nextInt(9000);
  }

  @override
  Widget build(BuildContext context) {
    final Map<String, dynamic> args =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    final String username = args['username'];
    final String email = args['email'];
    final String fullname = args['fullname'];
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text('Home Screen'),
          automaticallyImplyLeading: false,
          bottom: TabBar(
            tabs: [
              Tab(text: 'Home'),
              Tab(text: 'Manage'),
              Tab(text: 'About'),
            ],
          ),
        ),
        body: Stack(
          children: [
            TabBarView(
              children: [
                // Home tab
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Username: $username'),
                      SizedBox(height: 16),
                      Text('Email: $email'),
                      SizedBox(height: 16),
                      Text('Full Name:  $fullname'),
                      SizedBox(height: 16),
                      Center(
                        child: Image.asset('images/logo.png',
                            height: 200.0, width: 200.0),
                      ),
                      SizedBox(height: 16),
                      Text(
                          "Dropbox acts as a security hub in the middle of sellers and couriers; providing secured temporary storage for package drop-offs.\n\nIt is a self-service Dropbox that is accessible 24/7, where couriers can drop off users' orders for them to collect.\n\nDropbox makes package drop-off secure, efficient, and convenient for both users and couriers."),
                    ],
                  ),
                ),
                // Manage tab
                Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Generate OTP button
                      Container(
                        width: 300,
                        height: 70,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            primary: Colors.cyan,
                            textStyle: TextStyle(
                              fontSize: 20,
                            ),
                          ),
                          onPressed: () => _generateOTP(context, username),
                          child: Text('Generate OTP'),
                        ),
                      ),
                      SizedBox(height: 80),

// Accept button
                      Container(
                        width: 300,
                        height: 70,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            primary: Colors.green,
                            textStyle: TextStyle(
                              fontSize: 20,
                            ),
                          ),
                          onPressed: () => _acceptRequest(context, username),
                          child: Text('Accept'),
                        ),
                      ),
                      SizedBox(height: 80),

// Reject button
                      Container(
                        width: 300,
                        height: 70,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            primary: Colors.red,
                            textStyle: TextStyle(
                              fontSize: 20,
                            ),
                          ),
                          onPressed: () => _rejectRequest(context, username),
                          child: Text('Reject'),
                        ),
                      ),
                    ],
                  ),
                ),
                // About tab

                // About tab
                Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Image.asset('images/logo.png',
                            height: 100.0, width: 100.0),
                        SizedBox(height: 16),
                        Text(
                          "The company name is Dropbox, and the company logo is shown above. The logo resembles a Dropbox that represents security and innovation. Dropbox believes that the key to innovation is to start with an idea and materialize it by devoting time, knowledge, and resources. The color lavender represents purity, refinement, and devotion, which represent the team’s quality in making the company. The logo itself has transparent layers, which represent 2 layers of security in relation to the multi-modal method used as an authenticator.\n\nDropbox is a technology company that aims to provide modernized multi-modal biometric lockers in the country. Dropbox is located in Quezon City, Metro Manila, Philippines, and was founded in 2022 by the following Computer Engineering students: Joseph Allan Lopez, Gerald Maranan, Willord Plotena, Marjoulyn Ramirez, and Mark Daniel Ruiz.",
                          textAlign: TextAlign.justify,
                          style: TextStyle(
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            // Logout button at the bottom right corner
            Positioned(
              right: 16,
              bottom: 16,
              child: ElevatedButton(
                onPressed: () {
                  // Navigate back to the login form
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => LoginForm()),
                  );
                },
                child: Text('Logout'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class LoginForm extends StatefulWidget {
  @override
  _LoginFormState createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  final _formKey = GlobalKey<FormState>();
  String _email = '';
  String _password = '';
  void _clearForm() {
    setState(() {
      // Set the initial value of the password field to an empty string
      _email = '';
      _password = '';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: Text('Login'),
          automaticallyImplyLeading: false,
        ),
        body: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 16.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                SizedBox(height: 16),
                TextFormField(
                  decoration: InputDecoration(labelText: 'Username'),
                  validator: (value) {
                    if (value?.isEmpty ?? true) {
                      return 'Please enter your username';
                    }
                    return null;
                  },
                  onSaved: (value) {
                    _email = value!;
                  },
                  initialValue: '',
                ),
                SizedBox(height: 16),
                TextFormField(
                  decoration: InputDecoration(labelText: 'Password'),
                  obscureText: true,
                  validator: (value) {
                    if (value?.isEmpty ?? true) {
                      return 'Please enter your password';
                    }
                    return null;
                  },
                  onSaved: (value) {
                    _password = value!;
                  },
                  initialValue: '',
                ),
                SizedBox(height: 16.0),
                ElevatedButton(
                  child: Text('Login'),
                  onPressed: () async {
                    if (_formKey.currentState?.validate() ?? false) {
                      _formKey.currentState?.save();
                      // TODO: Call API to validate credentials and navigate to home page
                      var db = await mongo.Db.create(
                          'mongodb+srv://pdipbox:projectdesign2@cluster0.jqevhad.mongodb.net/dropbox?retryWrites=true&w=majority');
                      await db.open();
                      var coll = db.collection('userinfo');
                      var result = await coll
                          .findOne({'User': _email, 'Password': _password});
                      if (result == null) {
                        showDialog(
                          context: context,
                          builder: (BuildContext context) {
                            return AlertDialog(
                              title: Text('Invalid credentials'),
                              content: Text(
                                  'The username or password you entered is incorrect.'),
                              actions: <Widget>[
                                TextButton(
                                  child: Text('OK'),
                                  onPressed: () {
                                    Navigator.of(context).pop();
                                  },
                                ),
                              ],
                            );
                          },
                        );
                      } else {
                        Navigator.pushReplacementNamed(
                          context,
                          '/homescreen',
                          arguments: {
                            'username': _email,
                            'email': result['Email'],
                            'fullname': result['FullName']
                          },
                        );
                        _clearForm();
                      }
                    }
                  },
                ),
                SizedBox(height: 16.0),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/register');
                  },
                  child: Text('Create an Account'),
                ),
                SizedBox(height: 60),
                Image.asset('images/logo.png', height: 200.0, width: 200.0),
              ],
            ),
          ),
        ));
  }
}

class RegistrationForm extends StatefulWidget {
  @override
  _RegistrationFormState createState() => _RegistrationFormState();
}

class _RegistrationFormState extends State<RegistrationForm> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _fnameController = TextEditingController();

  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _fnameController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<bool> registerUser(
      String email, String fname, String username, String password) async {
    final db = await mongo.Db.create(
        'mongodb+srv://pdipbox:projectdesign2@cluster0.jqevhad.mongodb.net/dropbox?retryWrites=true&w=majority');
    await db.open();
    final collection = db.collection('userinfo');
    final user = await collection.findOne({'User': username});
    if (user == null) {
      await collection.insert({
        'User': username,
        'Password': password,
        'FullName': fname,
        'Email': email,
        'otp': '',
        'request_status': 'rejected'
      });
      return true;
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Create an Account'),
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              SizedBox(height: 16),
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(labelText: 'Email'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your email';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _fnameController,
                decoration: InputDecoration(labelText: 'Fullname'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your full name';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _usernameController,
                decoration: InputDecoration(labelText: 'Username'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your username';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(labelText: 'Password'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a password';
                  }
                  if (value.length < 6) {
                    return 'Password must be at least 6 characters long';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _confirmPasswordController,
                obscureText: true,
                decoration: InputDecoration(labelText: 'Confirm Password'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please confirm your password';
                  }
                  if (value != _passwordController.text) {
                    return 'Passwords do not match';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              SizedBox(height: 16.0),
              ElevatedButton(
                onPressed: () async {
                  if (_formKey.currentState!.validate()) {
                    final success = await registerUser(
                        _emailController.text,
                        _fnameController.text,
                        _usernameController.text,
                        _passwordController.text);
                    if (success) {
                      // Registration was successful, navigate to home screen
                      _emailController.clear();
                      _fnameController.clear();
                      _usernameController.clear();
                      _passwordController.clear();
                      _confirmPasswordController.clear();
                      Navigator.pushNamed(context, '/loginform');
                    } else {
                      // User already exists, show error message
                      showDialog(
                        context: context,
                        builder: (context) {
                          return AlertDialog(
                            title: Text('Registration Error'),
                            content: Text(
                                'A user with that username already exists. Please choose a different username.'),
                            actions: [
                              ElevatedButton(
                                onPressed: () => Navigator.pop(context),
                                child: Text('OK'),
                              ),
                            ],
                          );
                        },
                      );
                    }
                  }
                },
                child: Text('Register'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
