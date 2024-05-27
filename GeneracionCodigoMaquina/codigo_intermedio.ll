; ModuleID = "dependencia_principal"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define float @"main"()
{
main:
  %".2" = call float @"calcular_suma"(float 0x4008000000000000, i32 4)
  ret float %".2"
}

define float @"calcular_suma"(float %"a", i32 %"b")
{
function_body:
  %".4" = sitofp i32 %"b" to float
  %"resultado" = fadd float %"a", %".4"
  ret float %"resultado"
}
