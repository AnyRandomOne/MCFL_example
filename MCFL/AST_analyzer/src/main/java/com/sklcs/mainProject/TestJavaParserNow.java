package com.sklcs.mainProject;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.stmt.IfStmt;
import java.io.FileInputStream;

public class TestJavaParserNow {
	public static void main(String[] args) throws Exception{
		System.out.println("start TestJavaParserNow");
		//FileInputStream in = new FileInputStream(
		//		"/home/lizijie/research/new_work/javaparser-maven-sample/" +
		//				"src/main/java/com/sklcs/mainProject/"+args[0]+".java");
		// parse the file
		FileInputStream in = new FileInputStream(
				"/home/lizijie/research/new_work/" +
						"javaparser-maven-sample/InstrumentTester.java"
		);
		CompilationUnit cu = StaticJavaParser.parse(in);
		// prints the resulting compilation unit to default system output
		//System.out.println(cu.toString());
		cu.accept(new MethodVisitor(), null);
	}
       
	private static class MethodVisitor extends VoidVisitorAdapter<Void> {
		@Override
		public void visit(MethodDeclaration n, Void arg) {
			/* here you can access the attributes of the method.
		 this method will be called for all methods in this
		 CompilationUnit, including inner class methods */
			System.out.println("method:"+n.getName());
			System.out.println("method start: "+
					(n.getRange().isPresent()? n.getRange().get().startLine(): "none" ));
			//System.out.println("method token range: " + n.getTokenRange());
			super.visit(n, arg);
		}
	       
		@Override
		public void visit(ClassOrInterfaceDeclaration n, Void arg) {
			System.out.println("class:"+n.getName());
			System.out.println("extends:"+n.getExtendedTypes());
			System.out.println("implements:"+n.getImplementedTypes());
			super.visit(n, arg);
		}

		@Override
		public void visit(IfStmt n, Void arg){
			System.out.println("if stmt");
			System.out.println("condition: " + n.getCondition());
			System.out.println("if range: " + n.getRange());
			super.visit(n, arg);
		}

		@Override
		public void visit(PackageDeclaration n, Void arg) {
			System.out.println("package:"+n.getName());
			super.visit(n, arg);
		}
	}
}

