### Cálculo de Nonce

<p>A dificuldade de minerar bitcoins ocorre porque é necessário executar o que se chama de prova de trabalho. Em outras palavras, vários mineradores competem para realizar uma tarefa; aquele que primeiro realizar é o minerador campeão da atividade e recebe uma boa recompensa. Na prática, a atividade a realizar é: receber um conjunto de transações (um conjunto de bytes) e calcular o hash SHA-256 deles, mas tem um detalhe: um número de quatro bytes deve ser adicionado no início dos bytes recebidos (chame-o de <strong>nonce</strong>) e dos 256 bits de resultado uma determinada quantidade inicial deve ser zero.  O minerador que descobrir o nonce certo é o vencedor. Graficamente:</p>

<img width="990" height="102" alt="image" src="https://github.com/user-attachments/assets/7fe5256c-e5c5-4530-b91a-d3b0d6d27823" />

<p>Portanto, minerar é:</p>
<ol type:"a">
  <li>escolher um nonce de 4 bytes;</li>
  <li>juntar com os bytes da entrada (o nonce vem antes dos bytes de entrada);</li>
  <li>calcular o hash desse conjunto;</li>
  <li>verificar se o hash resultante inicia com uma certa quantidade de bits em zero;</li>
  <li>se o hash calculado não atende ao requisito, repetir o processo.</li>
</ol>

<p>Faça uma função em Python de nome <strong>findNonce</strong>striong> que recebe 2 argumentos:</p>
<ul>
  <li><strong>dataToHash</strong>: um conjunto de bytes;</li>
  <li><strong>bitsToBeZero</strong>: o número de bits iniciais que deve ser zero no hash.</li>
</ul>

<p>e devolve:</p>

<ul>
  <li>o <strong>nonce</strong> encontrado como um inteiro big endian;</li>
  <li>o <strong>tempo</strong> (em segundos) que demorou para encontrar o nonce</li>
</ul>

<p>Ao final, faça um programa que usa a função para preencher a seguinte tabela:</p>

<img width="900" height="278" alt="image" src="https://github.com/user-attachments/assets/2bf1f4f1-13e5-4991-9601-efebe5c8acf6" />

<p>Sua resposta deve ser 3 arquivos: um arquivo com o programa principal (<strong>questao1.py</strong>), um segundo com a função solicitada (e outras auxiliares se necessário) e o terceiro com a tabela preenchida (em formato csv).</p>