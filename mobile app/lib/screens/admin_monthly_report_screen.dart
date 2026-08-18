import 'package:flutter/material.dart';
import '../api_service.dart';
import 'employee_monthly_detail_screen.dart';

class AdminMonthlyReportScreen extends StatefulWidget {
  const AdminMonthlyReportScreen({super.key});

  @override
  State<AdminMonthlyReportScreen> createState() =>
      _AdminMonthlyReportScreenState();
}

class _AdminMonthlyReportScreenState
    extends State<AdminMonthlyReportScreen> {

  //=============================
  // FILTERS
  //=============================

  int selectedMonth = DateTime.now().month;
  int selectedYear = DateTime.now().year;

  String selectedDepartment = "All";

  final TextEditingController employeeIdController =
      TextEditingController();

  bool isLoading = false;

  //=============================
  // DATA
  //=============================

  List departments = [];

  List report = [];

  final List<String> months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
  ];

  final List<int> years =
      List.generate(6, (i) => DateTime.now().year - i);

  @override
  void initState() {
    super.initState();
    loadDepartments();
    generateReport();
  }

  //=============================
  // LOAD DEPARTMENTS
  //=============================

  Future<void> loadDepartments() async {

    try {

      final data = await ApiService.getDepartments();

      setState(() {

        departments = [
          {
            "department_name": "All"
          },
          ...data
        ];

      });

    } catch (e) {

      print("Department Error : $e");

    }

  }

  //=============================
  // GENERATE REPORT
  //=============================

  Future<void> generateReport() async {

    setState(() {

      isLoading = true;

    });

    try {

      final data =
          await ApiService.getMonthlyReport(

        selectedMonth,

        selectedYear,

        selectedDepartment,

        employeeId:
            employeeIdController.text.trim(),

      );

      setState(() {

        report = data;

      });

    } catch (e) {

      print(e);

      ScaffoldMessenger.of(context).showSnackBar(

        SnackBar(

          content: Text(e.toString()),

        ),

      );

    }

    setState(() {

      isLoading = false;

    });

  }

  //=============================
  // SUMMARY
  //=============================

  int get totalEmployees => report.length;

  int get totalPresent {

    int total = 0;

    for (var e in report) {

      total += int.tryParse(
              e["summary"]["present"].toString()) ??
          0;

    }

    return total;

  }

  int get totalAbsent {

    int total = 0;

    for (var e in report) {

      total += int.tryParse(
              e["absent"].toString()) ??
          0;

    }

    return total;

  }

  int get totalHalfDay {

    int total = 0;

    for (var e in report) {

      total += int.tryParse(
              e["half_day"].toString()) ??
          0;

    }

    return total;

  }

  int get totalLeave {

    int total = 0;

    for (var e in report) {

      total += int.tryParse(
              e["leave_days"].toString()) ??
          0;

    }

    return total;

  }

  int get totalHoliday {

    int total = 0;

    for (var e in report) {

      total += int.tryParse(
              e["holiday"].toString()) ??
          0;

    }

    return total;

  }

  int get totalWeeklyOff {

    int total = 0;

    for (var e in report) {

      total += int.tryParse(
              e["weekly_off"].toString()) ??
          0;

    }

    return total;

  }

    @override
    Widget build(BuildContext context) {

      return Scaffold(

        backgroundColor: const Color(0xffF5F7FB),

        appBar: AppBar(

          backgroundColor: Colors.indigo,

          elevation: 0,

          centerTitle: true,

          title: const Column(

            children: [

              Text(
                "Monthly Report",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),

              SizedBox(height: 2),

              Text(
                "Admin Panel",
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.normal,
                ),
              ),

            ],
          ),
        ),

        body: isLoading

            ? const Center(
                child: CircularProgressIndicator(),
              )

            : SingleChildScrollView(

                padding: const EdgeInsets.all(15),

                child: Column(

                  crossAxisAlignment:
                      CrossAxisAlignment.start,

                  children: [

                    buildFilterCard(),

                    const SizedBox(height:20),

                    SizedBox(

                      width: double.infinity,

                      height: 50,

                      child: ElevatedButton.icon(

                        style: ElevatedButton.styleFrom(

                          backgroundColor: Colors.indigo,

                          foregroundColor: Colors.white,

                          shape: RoundedRectangleBorder(

                            borderRadius:
                                BorderRadius.circular(12),

                          ),

                        ),

                        onPressed: generateReport,

                        icon: const Icon(Icons.search),

                        label: const Text(

                          "Generate Report",

                          style: TextStyle(
                            fontSize:16,
                          ),

                        ),

                      ),

                    ),

                    const SizedBox(height:15),

                    SizedBox(

                      width: double.infinity,

                      height: 50,

                      child: ElevatedButton.icon(

                        style: ElevatedButton.styleFrom(

                          backgroundColor: Colors.red,

                          foregroundColor: Colors.white,

                          shape: RoundedRectangleBorder(

                            borderRadius:
                                BorderRadius.circular(12),

                          ),

                        ),

                        onPressed: () async {
                          await ApiService.downloadMonthlyReportPDF(
                            selectedMonth,
                            selectedYear,
                          );
                        },

                        icon: const Icon(Icons.picture_as_pdf),

                        label: const Text(

                          "Download Report (PDF)",

                          style: TextStyle(
                            fontSize:16,
                          ),

                        ),

                      ),

                    ),

                    const SizedBox(height:25),

                    Row(

                      children: [

                        const Text(

                          "All Employees Report",

                          style: TextStyle(

                            fontWeight: FontWeight.bold,

                            fontSize:20,

                          ),

                        ),

                        const Spacer(),

                        Container(

                          padding: const EdgeInsets.symmetric(

                            horizontal: 14,

                            vertical: 8,

                          ),

                          decoration: BoxDecoration(

                            color: Colors.indigo,

                            borderRadius:
                                BorderRadius.circular(20),

                          ),

                          child: Text(

                            "Total : $totalEmployees",

                            style: const TextStyle(

                              color: Colors.white,

                              fontWeight: FontWeight.bold,

                            ),

                          ),

                        ),

                      ],

                    ),

                    const SizedBox(height:20),

                    buildReportTable(),

                    const SizedBox(height:25),

                    buildLegend(),

                  ],

                ),

              ),

      );

    }

    Widget buildFilterCard() {

      return Card(

        elevation: 3,

        shape: RoundedRectangleBorder(

          borderRadius:
              BorderRadius.circular(18),

        ),

        child: Padding(

          padding: const EdgeInsets.all(18),

          child: Column(

            children: [

              Row(

                children: [

                  Expanded(

                    child: DropdownButtonFormField<int>(

                      value: selectedMonth,

                      decoration: const InputDecoration(

                        labelText: "Month",

                        border: OutlineInputBorder(),

                      ),

                      items: List.generate(

                        12,

                        (i) => DropdownMenuItem(

                          value: i + 1,

                          child: Text(months[i]),

                        ),

                      ),

                      onChanged: (v) {

                        setState(() {

                          selectedMonth = v!;

                        });

                      },

                    ),

                  ),

                  const SizedBox(width:12),

                  Expanded(

                    child: DropdownButtonFormField<int>(

                      value: selectedYear,

                      decoration: const InputDecoration(

                        labelText: "Year",

                        border: OutlineInputBorder(),

                      ),

                      items: years.map((e){

                        return DropdownMenuItem(

                          value: e,

                          child: Text(e.toString()),

                        );

                      }).toList(),

                      onChanged: (v){

                        setState((){

                          selectedYear=v!;

                        });

                      },

                    ),

                  ),

                ],

              ),

              const SizedBox(height:15),

              Row(

                children: [

                  Expanded(

                    child: TextField(

                      controller:
                          employeeIdController,

                      keyboardType:
                          TextInputType.number,

                      decoration:
                          const InputDecoration(

                        labelText:
                            "Employee ID",

                        border:
                            OutlineInputBorder(),

                      ),

                    ),

                  ),

                  const SizedBox(width:12),

                  Expanded(

                    child:
                        DropdownButtonFormField<String>(

                      value: selectedDepartment,

                      decoration:
                          const InputDecoration(

                        labelText: "Department",

                        border:
                            OutlineInputBorder(),

                      ),

                      items: departments.map((dept){

                        return DropdownMenuItem<String>(

                          value: dept["department_name"].toString(),

                          child: Text(
                            dept["department_name"].toString(),
                          ),

                        );

                      }).toList(),

                      onChanged:(v){

                        setState((){

                          selectedDepartment=v!;

                        });

                      },

                    ),

                  ),

                ],

              ),

            ],

          ),

        ),

      );

    }
    Widget buildSummaryRow() {

      return Row(

        children: [

          Expanded(
            child: statCard(
              "Present",
              totalPresent.toString(),
              Colors.green,
            ),
          ),

          const SizedBox(width:10),

          Expanded(
            child: statCard(
              "Absent",
              totalAbsent.toString(),
              Colors.red,
            ),
          ),

          const SizedBox(width:10),

          Expanded(
            child: statCard(
              "Leave",
              totalLeave.toString(),
              Colors.orange,
            ),
          ),

        ],

      );

    }

    Widget statCard(

    String title,
    String value,
    Color color,

    ){

    return Card(

    elevation:2,

    shape: RoundedRectangleBorder(

    borderRadius:
    BorderRadius.circular(15),

    ),

    child:Padding(

    padding:
    const EdgeInsets.all(15),

    child:Column(

    children:[

    Text(

    value,

    style:TextStyle(

    fontSize:24,

    fontWeight:
    FontWeight.bold,

    color:color,

    ),

    ),

    const SizedBox(height:5),

    Text(title),

    ],

    ),

    ),

    );

    }

    Widget buildReportTable() {

    if(report.isEmpty){

    return const Card(

    child:SizedBox(

    height:200,

    child:Center(

    child:Text(

    "No Employee Found",

    style:TextStyle(fontSize:18),

    ),

    ),

    ),

    );

    }

    return Column(

    children:

    report.map((emp){

    String name =
    emp["employee_name"] ?? "";

    String code =
    emp["employee_code"] ?? "";

    String department =
    emp["department"] ?? "";

    String initials = "NA";


    if(name.trim().isNotEmpty){

      List<String> parts =
          name.trim().split(" ");


      initials =
          parts[0].substring(0,1).toUpperCase();


      if(parts.length > 1 &&
        parts[1].isNotEmpty){

        initials +=
            parts[1].substring(0,1).toUpperCase();

      }

    }

    return Card(

    margin:
    const EdgeInsets.only(bottom:15),

    shape:RoundedRectangleBorder(

    borderRadius:
    BorderRadius.circular(18),

    ),

    elevation:3,

    child:InkWell(

    borderRadius:
    BorderRadius.circular(18),

    onTap:(){

    Navigator.push(

    context,

    MaterialPageRoute(

    builder:(_)=>EmployeeMonthlyDetailScreen(

    employeeId:
    emp["employee_id"],

    employeeName:
    name,

    month:
    selectedMonth,

    year:
    selectedYear,

    ),

    ),

    );

    },

    child:Padding(

    padding:
    const EdgeInsets.all(15),

    child:Column(

    children:[

    Row(

    children:[

    CircleAvatar(

    radius:28,

    backgroundColor:
    Colors.indigo,

    child:Text(

    initials,

    style:
    const TextStyle(

    color:Colors.white,

    fontWeight:
    FontWeight.bold,

    ),

    ),

    ),

    const SizedBox(width:15),

    Expanded(

    child:Column(

    crossAxisAlignment:
    CrossAxisAlignment.start,

    children:[

    Text(

    code,

    style:
    const TextStyle(

    fontSize:13,

    color:Colors.grey,

    ),

    ),

    const SizedBox(height:3),

    Text(

    name,

    style:
    const TextStyle(

    fontWeight:
    FontWeight.bold,

    fontSize:18,

    ),

    ),

    Text(

    department,

    style:
    const TextStyle(

    color:Colors.grey,

    ),

    ),

    ],

    ),

    ),

    const Icon(

    Icons.arrow_forward_ios,

    size:18,

    ),

    ],

    ),

    const SizedBox(height:18),

    Row(

    mainAxisAlignment:
    MainAxisAlignment.spaceEvenly,

    children:[

    statusBox(
    "P",
    emp["summary"]["present"].toString(),
    Colors.green
    ),

    statusBox("HD",
    emp["summary"]["half_day"].toString(),
    Colors.orange),

    statusBox("A",
    emp["summary"]["absent"].toString(),
    Colors.red),

    statusBox("L",
    emp["summary"]["leave"].toString(),
    Colors.blue),

    statusBox("H",
    emp["summary"]["holiday"].toString(),
    Colors.purple),

    statusBox("WO",
    emp["summary"]["weekly_off"].toString(),
    Colors.teal),

    ],

    ),

    ],

    ),

    ),

    ),

    );

    }).toList(),

    );

    }

    Widget statusBox(

    String title,

    String value,

    Color color,

    ){

    return Container(

    width:50,

    padding:
    const EdgeInsets.symmetric(

    vertical:8,

    ),

    decoration:BoxDecoration(

    color:color.withOpacity(.12),

    borderRadius:
    BorderRadius.circular(10),

    ),

    child:Column(

    children:[

    Text(

    title,

    style:TextStyle(

    color:color,

    fontWeight:
    FontWeight.bold,

    ),

    ),

    const SizedBox(height:5),

    Text(

    value,

    style:
    const TextStyle(

    fontWeight:
    FontWeight.bold,

    fontSize:16,

    ),

    ),

    ],

    ),

    );

    }

    Widget buildLegend(){

    return Card(

    child:Padding(

    padding:
    const EdgeInsets.all(15),

    child:Wrap(

    spacing:15,

    runSpacing:10,

    children:[

    legend("P","Present"),

    legend("HD","Half Day"),

    legend("A","Absent"),

    legend("L","Leave"),

    legend("H","Holiday"),

    legend("WO","Weekly Off"),

    ],

    ),

    ),

    );

    }

    Widget legend(

    String short,

    String full,

    ){

    return Row(

    mainAxisSize:
    MainAxisSize.min,

    children:[

    Container(

    padding:
    const EdgeInsets.symmetric(

    horizontal:10,

    vertical:5,

    ),

    decoration:BoxDecoration(

    color:Colors.indigo,

    borderRadius:
    BorderRadius.circular(8),

    ),

    child:Text(

    short,

    style:
    const TextStyle(

    color:Colors.white,

    ),

    ),

    ),

    const SizedBox(width:8),

    Text(full),

    ],

    );

    }
}    