Module(
    body=[
        FunctionDef(
            name='factorial',
            args=arguments(
                posonlyargs=[],
                args=[
                    arg(
                        arg='n',
                        annotation=Name(id='int', ctx=Load())),
                    arg(
                        arg='n2',
                        annotation=Name(id='int', ctx=Load()))],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]),
            body=[
                If(
                    test=BoolOp(
                        op=Or(),
                        values=[
                            Compare(
                                left=Name(id='n', ctx=Load()),
                                ops=[
                                    Eq()],
                                comparators=[
                                    Constant(value=0)]),
                            Compare(
                                left=Name(id='n', ctx=Load()),
                                ops=[
                                    Eq()],
                                comparators=[
                                    Constant(value=1)])]),
                    body=[
                        Return(
                            value=Constant(value=1))],
                    orelse=[]),
                Return(
                    value=Tuple(
                        elts=[
                            Constant(value='la respuesta es'),
                            BinOp(
                                left=Name(id='n', ctx=Load()),
                                op=Mult(),
                                right=Call(
                                    func=Name(id='factorial', ctx=Load()),
                                    args=[
                                        BinOp(
                                            left=Name(id='n', ctx=Load()),
                                            op=Sub(),
                                            right=Constant(value=1))],
                                    keywords=[]))],
                        ctx=Load()))],
            decorator_list=[],
            returns=Name(id='int', ctx=Load())),
        Expr(
            value=Call(
                func=Name(id='print', ctx=Load()),
                args=[
                    Call(
                        func=Name(id='factorial', ctx=Load()),
                        args=[
                            Constant(value=9)],
                        keywords=[])],
                keywords=[]))],
    type_ignores=[])