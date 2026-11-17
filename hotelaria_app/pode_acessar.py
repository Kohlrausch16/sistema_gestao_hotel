def pode_acessar(user, nome_view):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    funcionario = getattr(user, 'funcionario', None)
    cargo = funcionario.cargo if funcionario else None
    if cargo == 'gerente':
        return True

    acessos = {
                'recepcionista': [
                    'index', 'listar_clientes', 'cadastrar_cliente', 'editar_cliente',
                    'excluir_cliente',
                    'listar_quartos', 'cadastrar_quarto', 'editar_quarto',
                    'excluir_quarto', 'quartos_disponiveis',
                    'listar_reservas', 'criar_reserva', 'editar_reserva',
                    'cancelar_reserva', 'checkin_page', 'checkin', 'checkout',
                    'checkincheckout',
                    'listar_ocorrencia', 'registrar_ocorrencia',
                    'visualizar_ocorrencia', 'concluir_ocorrencia',
                    'ocorrencias_concluidas', 'reabrir_ocorrencia',
                    'gerar_relatorio',
                ],
                'cozinheiro': [
                    'index', 'listar_reservas', 'quartos_disponiveis',
                    'listar_ocorrencia', 'registrar_ocorrencia',
                    'visualizar_ocorrencia', 'concluir_ocorrencia',
                    'ocorrencias_concluidas', 'reabrir_ocorrencia',
                ],
                'camareira': [
                    'index', 'listar_quartos', 'editar_quarto',
                    'quartos_disponiveis',
                    'listar_ocorrencia', 'registrar_ocorrencia',
                    'visualizar_ocorrencia', 'concluir_ocorrencia',
                    'ocorrencias_concluidas', 'reabrir_ocorrencia',
                    'listar_reservas',
                ],
            }
    if (cargo in acessos):
        return nome_view in acessos[cargo]
    return False
