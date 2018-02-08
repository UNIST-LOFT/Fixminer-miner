package edu.lu.uni.serval.FixPattern.utils;

import java.util.HashMap;
import java.util.Map;

public class CNodeMap {
	
	public static Map<Integer, String> map;
	
	static {
		map  = new HashMap<Integer, String>();
		map.put(240500, "CondExpr");
		map.put(240400, "FunCall");
		map.put(241800, "StatementExpr");
		map.put(241300, "RecordAccess");
		map.put(420100, "DefineExpr");
		map.put(290001, "None");
		map.put(350200, "MacroDecl");
		map.put(280100, "Goto");
		map.put(60100, "BaseType");
		map.put(410001, "DefineVar");
		map.put(420200, "DefineStmt");
		map.put(450800, "FinalDef");
		map.put(260300, "ExprStatement");
		map.put(340000, "Storage");
		map.put(290100, "Some");
		map.put(410100, "DefineFunc");
		map.put(420400, "DefineDoWhileZero");
		map.put(70100, "IntType");
		map.put(20100, "Left");
		map.put(480000, "GenericString");
		map.put(241600, "SizeOfType");
		map.put(241000, "Unary");
		map.put(300100, "If");
		map.put(450300, "CppTop");
		map.put(460000, "Program");
		map.put(241200, "ArrayAccess");
		map.put(450400, "IfdefTop");
		map.put(330000, "Compound");
		map.put(310200, "DoWhile");
		map.put(240700, "Assignment");
		map.put(270100, "Label");
		map.put(360100, "InitExpr");
		map.put(270400, "Default");
		map.put(450600, "EmptyDef");
		map.put(470000, "GenericList");
		map.put(490100, "IfToken");
		map.put(60900, "StructUnionName");
		map.put(240600, "Sequence");
		map.put(80100, "Si");
		map.put(360200, "InitList");
		map.put(370200, "DesignatorIndex");
		map.put(360300, "InitDesignators");
		map.put(280001, "Continue");
		map.put(420001, "DefineEmpty");
		map.put(310100, "While");
		map.put(270200, "Case");
		map.put(450700, "NotParsedCorrectly");
		map.put(400100, "Define");
		map.put(370100, "DesignatorField");
		map.put(280003, "Return");
		map.put(240800, "Postfix");
		map.put(100003, "CInt");
		map.put(240100, "Ident");
		map.put(310300, "For");
		map.put(400200, "Include");
		map.put(440100, "IfdefDirective");
		map.put(220100, "ParameterType");
		map.put(242000, "ParenExpr");
		map.put(200000, "ParamList");
		map.put(280002, "Break");
		map.put(241500, "SizeOfExpr");
		map.put(241400, "RecordPtAccess");
		map.put(380000, "Definition");
		map.put(50000, "TypeQualifier");
		map.put(450100, "Declaration");
		map.put(240900, "Infix");
		map.put(241100, "Binary");
		map.put(40000, "FullType");
		map.put(450200, "Definition");
		map.put(310400, "MacroIteration");
		map.put(280200, "ReturnExpr");
		map.put(300200, "Switch");
		map.put(350100, "DeclList");
		map.put(240200, "Constant");
		map.put(241700, "Cast");
	}
}
