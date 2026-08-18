import 'dart:html' as html;

void downloadPdfWeb(String url) {
  final anchor = html.AnchorElement(href: url)
    ..setAttribute(
      'download',
      'Monthly_Attendance_Report.pdf',
    )
    ..style.display = 'none';

  html.document.body!.children.add(anchor);

  anchor.click();

  anchor.remove();
}